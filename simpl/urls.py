from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from simpl.schema import schema

from . import views

urlpatterns = [
    path(
        "graphql/",
        csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True)),
        name="simpl-api",
    ),
    path("<int:pk>/", views.InitialView.as_view(), name="simpl"),
    path("<int:pk>/status/", views.StatusView.as_view(), name="simpl.status"),
    path("<int:pk>/configure/", views.ConfigView.as_view(), name="simpl.config"),
    path("<int:pk>/team/", views.TeamView.as_view(), name="simpl.team"),
    path("<int:pk>/players/", views.PlayersView.as_view(), name="simpl.players"),
    path("<int:pk>/start/", views.StartView.as_view(), name="simpl.start"),
    path("<int:pk>/debrief/", views.DebriefView.as_view(), name="simpl.debrief"),
    path("<int:pk>/end/", views.EndGameplayView.as_view(), name="simpl.end"),
]
