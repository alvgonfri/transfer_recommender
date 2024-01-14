from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import Player, Team
from .forms import (
    LoginForm,
    PlayerForm,
    TeamForm,
    PositionNeededAndMaxAverageAgeForm,
    TeamAndValueForm,
    PhraseForm,
    PlayerAndPositionForm,
)
from .populate import populate_database
from .whoosh import (
    store_data,
    list_teams,
    list_players,
    teams_by_position_needed_and_max_average_age,
    players_by_team_and_value,
    players_by_name_or_nationality,
    update_position,
)
from .recommendations import (
    load_similarities,
    recommend_teams,
    recommend_players,
    similar_teams,
    similar_players,
)


def home(request):
    return render(request, "base/home.html")


@login_required(login_url="/login")
def populate(request):
    populate_database()
    messages.success(request, "¡Datos cargados correctamente!")
    return render(request, "base/home.html")


@login_required(login_url="/login")
def load_index(request):
    store_data()
    messages.success(request, "¡Índice cargado correctamente!")
    return render(request, "base/home.html")


@login_required(login_url="/login")
def load_RS(request):
    load_similarities()
    messages.success(request, "¡Sistema de recomendación cargado correctamente!")
    return render(request, "base/home.html")


def list_teams_view(request):
    teams = list_teams()
    tags = {}
    for team in teams:
        tags[team["name"]] = team["tags"].split(",")
    return render(request, "base/list_teams.html", {"teams": teams, "tags": tags})


def list_players_view(request):
    players = list_players()
    tags = {}
    for player in players:
        tags[player["name"]] = player["tags"].split(",")
    return render(request, "base/list_players.html", {"players": players, "tags": tags})


def teams_by_position_needed_and_max_average_age_view(request):
    if request.method == "POST":
        form = PositionNeededAndMaxAverageAgeForm(request.POST)
        if form.is_valid():
            position = form.cleaned_data["position"]
            max_age = form.cleaned_data["max_age"]
            teams = teams_by_position_needed_and_max_average_age(position, max_age)
            tags = {}
            for team in teams:
                tags[team.name] = team.tags.all()
            return render(
                request,
                "base/teams_by_position_needed_and_max_average_age.html",
                {"teams": teams, "tags": tags, "form": form},
            )
    else:
        form = PositionNeededAndMaxAverageAgeForm()
    return render(
        request,
        "base/teams_by_position_needed_and_max_average_age.html",
        {"form": form},
    )


def players_by_team_and_value_view(request):
    if request.method == "POST":
        form = TeamAndValueForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data["team"]
            min_value = form.cleaned_data["min_value"]
            max_value = form.cleaned_data["max_value"]
            players = players_by_team_and_value(team, min_value, max_value)
            tags = {}
            for player in players:
                tags[player.name] = player.tags.all()
            return render(
                request,
                "base/players_by_team_and_value.html",
                {"players": players, "tags": tags, "form": form},
            )
    else:
        form = TeamAndValueForm()
    return render(request, "base/players_by_team_and_value.html", {"form": form})


def players_by_name_or_nationality_view(request):
    if request.method == "POST":
        form = PhraseForm(request.POST)
        if form.is_valid():
            phrase = form.cleaned_data["phrase"]
            players = players_by_name_or_nationality(phrase)
            tags = {}
            for player in players:
                tags[player.name] = player.tags.all()
            return render(
                request,
                "base/players_by_name_or_nationality.html",
                {"players": players, "tags": tags, "form": form},
            )
    else:
        form = PhraseForm()
    return render(request, "base/players_by_name_or_nationality.html", {"form": form})


def update_position_view(request):
    if request.method == "POST":
        form = PlayerAndPositionForm(request.POST)
        if form.is_valid():
            player = form.cleaned_data["player"]
            position = form.cleaned_data["position"]
            player_in_db = update_position(player, position)
            return render(
                request,
                "base/update_position.html",
                {
                    "player": player_in_db,
                    "form": form,
                },
            )
    else:
        form = PlayerAndPositionForm()
    return render(request, "base/update_position.html", {"form": form})


def recommend_teams_view(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.cleaned_data["player"]
            recommended_teams = recommend_teams(player)
            teams = []
            for team in recommended_teams:
                teams.append(Team.objects.get(name=team[0]))
            return render(
                request,
                "base/recommend_teams.html",
                {"teams": teams, "player": player, "form": form},
            )
    else:
        form = PlayerForm()
    return render(request, "base/recommend_teams.html", {"form": form})


def recommend_players_view(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data["team"]
            recommended_players = recommend_players(team)
            players = []
            for player_tuple in recommended_players:
                players.append(Player.objects.get(pk=player_tuple[0][0]))
            return render(
                request,
                "base/recommend_players.html",
                {"players": players, "team": team, "form": form},
            )
    else:
        form = TeamForm()
    return render(request, "base/recommend_players.html", {"form": form})


def similar_teams_view(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data["team"]
            similar_teams_list = similar_teams(team)
            teams = []
            for similar_team in similar_teams_list:
                teams.append(Team.objects.get(name=similar_team[0]))
            return render(
                request,
                "base/similar_teams.html",
                {"teams": teams, "team": team, "form": form},
            )
    else:
        form = TeamForm()
    return render(request, "base/similar_teams.html", {"form": form})


def similar_players_view(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.cleaned_data["player"]
            similar_players_list = similar_players(player)
            players = []
            for player_tuple in similar_players_list:
                players.append(Player.objects.get(pk=player_tuple[0][0]))
            return render(
                request,
                "base/similar_players.html",
                {"players": players, "player": player, "form": form},
            )
    else:
        form = PlayerForm()
    return render(request, "base/similar_players.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return render(request, "base/home.html")
    else:
        form = LoginForm()
    return render(request, "base/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return render(request, "base/home.html")
