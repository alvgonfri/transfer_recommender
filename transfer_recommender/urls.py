"""
URL configuration for transfer_recommender project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("populate/", views.populate, name="populate"),
    path("load_index/", views.load_index, name="load_index"),
    path("load_RS/", views.load_RS, name="load_RS"),
    path("list_teams/", views.list_teams_view, name="list_teams"),
    path("list_players/", views.list_players_view, name="list_players"),
    path(
        "position_needed_and_max_average_age/",
        views.teams_by_position_needed_and_max_average_age_view,
        name="teams_by_position_needed_and_max_average_age",
    ),
    path(
        "team_and_value/",
        views.players_by_team_and_value_view,
        name="players_by_team_and_value",
    ),
    path(
        "name_or_nationality/",
        views.players_by_name_or_nationality_view,
        name="players_by_name_or_nationality",
    ),
    path("update_position/", views.update_position_view, name="update_position"),
    path("recommend_teams/", views.recommend_teams_view, name="recommend_teams"),
    path("recommend_players/", views.recommend_players_view, name="recommend_players"),
    path("similar_teams/", views.similar_teams_view, name="similar_teams"),
    path("similar_players/", views.similar_players_view, name="similar_players"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
