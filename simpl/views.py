from typing import ClassVar, Optional

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic import DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin

from simpl import conf, get_run_model, nav

from . import models


class AuthProviderLoginRequiredMixin(LoginRequiredMixin):
    def get_login_url(self):
        login_url = super().get_login_url()
        provider = self.request.GET.get("provider", "")
        return f"{login_url}?provider={provider}" if provider else login_url


class SimplMixin(
    UserPassesTestMixin, AuthProviderLoginRequiredMixin, SingleObjectMixin
):
    simpl_name: ClassVar[Optional[str]] = None

    def get_queryset(self):
        model = get_run_model()
        return model._default_manager.all()

    @cached_property
    def run(self) -> models.Run:
        return getattr(self, "object", self.get_object())

    @cached_property
    def nav_data(self):
        return nav.get_nav(self.run)

    def test_func(self):
        user = self.request.user
        return user.is_superuser or self.run.managers.filter(pk=user.pk).exists()

    def get_template_names(self):
        template_names = super().get_template_names()
        if self.simpl_name and not self.template_name:
            template_names.insert(0, f"simpl/run_{self.simpl_name}.html")
        return template_names

    def dispatch(self, request, *args, **kwargs):
        if self.simpl_name:
            if (
                self.simpl_name not in self.nav_data
                or self.nav_data[self.simpl_name].status == nav.NavStatus.DISABLED
            ):
                raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs["simpl_current_nav"] = self.simpl_name
        kwargs["simpl_configuring"] = nav.is_configuring(self.run)
        kwargs["simpl_nav"] = self.nav_data
        kwargs["simpl_logout_url"] = reverse(
            getattr(conf.settings, "SIMPL_LOGOUT_URL_NAME", "logout")
        )
        for status in nav.NavStatus:
            kwargs[f"NAV_{status.name}"] = status
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        if self.simpl_name:
            return nav.get_next_url(self.run, self.simpl_name)
        return super().get_success_url()


class InitialView(SingleObjectMixin, RedirectView):
    def get_queryset(self):
        model = get_run_model()
        return model._default_manager.all()

    def get_redirect_url(self, *args, **kwargs):
        run = self.get_object()
        data = nav.get_nav(run)
        if not data:
            raise Http404()
        return list(data.values())[0].url


class StatusView(SimplMixin, DetailView):
    simpl_name = "status"

    def get_context_data(self, **kwargs):
        kwargs["configured"] = True
        kwargs["next_item"] = nav.get_next_item(self.run, self.simpl_name)
        return super().get_context_data(**kwargs)


class ConfigView(SimplMixin, DetailView):
    simpl_name = "config"


class TeamView(SimplMixin, DetailView):
    simpl_name = "team"


class PlayersView(SimplMixin, DetailView):
    simpl_name = "players"

    def get_queryset(self):
        model = get_run_model()
        return model._default_manager.prefetch_related(
            "player_set__character__instance",
            "player_set__user",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players = self.run.player_set.all().active().has_user()
        if self.run.status >= self.run.STATUS.PLAY:
            players = players.exclude(character__instance=None)
            if self.run.multiplayer:
                teams = {}
                for player in players:
                    teams.setdefault(player.character.instance.name, [])
                    teams[player.character.instance.name].append(player)
                context["teams"] = teams
        context["players"] = players
        context["inactive_players"] = self.run.player_set.all().inactive()
        context["invites"] = self.run.player_set.all().active().has_user(False)
        if len(context.get("simpl_nav", {})) > 1 and context.get("simpl_configuring"):
            context["next_url"] = nav.get_next_url(self.run, self.simpl_name)
        return context


class StartView(SimplMixin, DetailView):
    simpl_name = "start"

    @cached_property
    def ready(self):
        return (
            self.run.multiplayer is False
            or not self.run.player_set.unbalanced().exists()
        )

    def get_context_data(self, **kwargs):
        kwargs["ready"] = self.ready
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        run = self.run
        if self.ready and run.status in (run.STATUS.SETUP, run.STATUS.PREPARE):
            run.lobby_set.update(ready=True)
            instances = run.prepare()
            run.start_instances(instances)
            run.status = run.STATUS.PLAY
            run.save()
        return redirect(self.get_success_url())


class DebriefView(SimplMixin, DetailView):
    template_name = "simpl/run_debrief.html"

    def post(self, request, *args, **kwargs):
        if self.run.status == self.run.STATUS.PLAY:
            self.run.status = self.run.STATUS.DEBRIEF
            message = "Player reports have been published."
        elif self.run.status == self.run.STATUS.DEBRIEF:
            self.run.status = self.run.STATUS.PLAY
            message = "Player reports have been hidden."
        self.run.save()
        messages.success(request, message)
        url = request.POST.get("redirect_to") or nav.get_next_url(
            self.run, self.simpl_name
        )
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        kwargs["redirect_to"] = self.request.GET.get("redirect_to")
        return super().get_context_data(**kwargs)


class EndGameplayView(SimplMixin, DetailView):
    template_name = "simpl/run_end_gameplay.html"
    simpl_name = "end"

    def post(self, request, *args, **kwargs):
        if not self.run.ended:
            self.run.instances.update(date_end=timezone.now())
            message = (
                "The game has ended for all players. "
                "Select Restart Game to continue gameplay."
            )
        else:
            self.run.instances.update(date_end=None)
            message = "The game has been restarted."
        messages.success(request, message)
        url = request.POST.get("redirect_to") or nav.get_next_url(
            self.run, self.simpl_name
        )
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        kwargs["redirect_to"] = self.request.GET.get("redirect_to")
        return super().get_context_data(**kwargs)
