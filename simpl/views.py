import csv
from typing import ClassVar, Optional

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin

from simpl import conf, get_run_model, get_player_model, nav

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
        provider = self.request.GET.get("provider", "")
        url = list(data.values())[0].url
        return f"{url}?provider={provider}" if provider else url


class StatusView(SimplMixin, DetailView):
    simpl_name = "status"

    @cached_property
    def ready(self):
        return (
            self.run.multiplayer is False
            or not self.run.player_set.unbalanced().exists()
        )

    def get_context_data(self, **kwargs):
        kwargs["ready"] = self.ready
        kwargs["configured"] = True
        kwargs["next_item"] = nav.get_next_item(self.run, self.simpl_name)
        return super().get_context_data(**kwargs)


class ConfigView(SimplMixin, DetailView):
    simpl_name = "config"


class TeamView(SimplMixin, DetailView):
    simpl_name = "team"


class PlayersView(SimplMixin, DetailView):
    simpl_name = "players"

    def get_players_queryset(self):
        return self.run.player_set.select_related(
            "user", "character__instance"
        ).order_by("user__first_name", "user__last_name")

    def filter_players_queryset(self, players_queryset):
        search = self.request.GET.get("q")
        if search:
            players_queryset = players_queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
            )
        return players_queryset

    def get_active_players(self, players_queryset):
        players = players_queryset.active().has_user()
        if self.run.status >= self.run.STATUS.PLAY:
            players = players.exclude(character__instance=None)
        count = players.count()
        return count, self.filter_players_queryset(players)

    def get_inactive_players(self, players_queryset):
        players = players_queryset.inactive()
        return players.count(), self.filter_players_queryset(players)

    def get_invited_players(self, players_queryset):
        players = players_queryset.active().has_user(False)
        return players.count(), self.filter_players_queryset(players)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players_qs = self.get_players_queryset()

        active_count, active_players = self.get_active_players(players_qs)
        if self.run.multiplayer:
            teams = {}
            for player in active_players:
                teams.setdefault(player.character.instance.name, [])
                teams[player.character.instance.name].append(player)
            context["teams"] = teams
        context["players"] = active_players
        context["players_count"] = active_count

        inactive_count, inactive_players = self.get_inactive_players(players_qs)
        context["inactive_players"] = inactive_players
        context["inactive_count"] = inactive_count

        invites_count, invited_players = self.get_invited_players(players_qs)
        context["invites"] = invited_players
        context["invites_count"] = invites_count

        if len(context.get("simpl_nav", {})) > 1 and context.get("simpl_configuring"):
            context["next_url"] = nav.get_next_url(self.run, self.simpl_name)
        return context

    def post(self, request, **kwargs):
        Player = get_player_model()
        deactivate = request.POST.getlist("deactivate")
        if deactivate:
            Player.objects.filter(pk__in=deactivate).update(inactive=True)
        reactivate = request.POST.getlist("reactivate")
        if reactivate:
            Player.objects.filter(pk__in=reactivate).update(inactive=False)
        return redirect(".")


class DownloadPlayers(SimplMixin, DetailView):
    def get(self, request, *args, **kwargs):
        filename = self.run.name.replace(' ', '')
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}.csv"'},
        )
        team_field = ["Team"] if self.run.multiplayer else []
        fieldnames = team_field + ["Name", "Inactive"]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        order_by_team = ["character__instance__name"] if self.run.multiplayer else []
        players = self.run.player_set.select_related(
            "lobby", "character__instance", "user"
        ).order_by(*order_by_team, "user__first_name", "user__last_name")

        for player in players:
            row = {
                "Name": player.public_name,
                "Inactive": "Yes" if player.inactive else "",
            }
            if self.run.multiplayer:
                row["Team"] = player.team_name
            writer.writerow(row)

        return response


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
            instances = run.prepare()
            run.start_instances(instances)
            run.status = run.STATUS.PLAY
            run.save()
        return redirect(self.get_success_url())


class DebriefView(SimplMixin, DetailView):
    template_name = "simpl/run_debrief.html"

    def post(self, request, *args, **kwargs):
        if self.run.status == self.run.STATUS.DEBRIEF:
            self.run.status = (
                self.run.STATUS.COMPLETE if self.run.ended else self.run.STATUS.PLAY
            )
            message = "Player reports have been hidden."
        else:
            self.run.status = self.run.STATUS.DEBRIEF
            message = "Player reports have been published."
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
        stoped_msg = "The game has been stopped for all players."
        started_msg = "The game has been restarted."
        if self.run.instances:
            if self.run.running_instances:  # end run
                for instance in self.run.running_instances:
                    instance.stop()
                message = stoped_msg
                if self.run.status == self.run.STATUS.PLAY:
                    self.run.status = self.run.STATUS.COMPLETE
                # DEBRIEF and COMPLETE statuses remain the same
            else:  # restart
                for instance in self.run.ended_instances:
                    instance.restart()
                message = started_msg
                if self.run.status == self.run.STATUS.COMPLETE:
                    self.run.status = self.run.STATUS.PLAY
                # DEBRIEF and PLAY statuses remain the same
            self.run.save()
        else:
            message = "Wait for players to sign up to proceed to the next step."

        messages.success(request, message)
        url = request.POST.get("redirect_to") or nav.get_next_url(
            self.run, self.simpl_name
        )
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        kwargs["redirect_to"] = self.request.GET.get("redirect_to")
        return super().get_context_data(**kwargs)
