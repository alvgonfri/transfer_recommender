import os
import shutil
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import NumericRange
from .models import Tag, Player, Team
from .populate import set_tags, populate_tags

TEAM_INDEX_DIR = "main/team_index"
PLAYER_INDEX_DIR = "main/player_index"


def store_data():
    team_schema = Schema(
        id=ID(stored=True, unique=True),
        name=TEXT(stored=True, phrase=False),
        market_value=NUMERIC(stored=True),
        average_age=NUMERIC(stored=True),
        foreigner_percentage=NUMERIC(stored=True),
        goalkeepers=NUMERIC(stored=True),
        defenders=NUMERIC(stored=True),
        midfielders=NUMERIC(stored=True),
        forwards=NUMERIC(stored=True),
        logoURL=ID(stored=True),
        tags=KEYWORD(stored=True, commas=True),
    )

    player_schema = Schema(
        id=ID(stored=True, unique=True),
        name=TEXT(stored=True),
        team=TEXT(stored=True, phrase=False),
        age=NUMERIC(stored=True),
        nationality=TEXT(stored=True),
        position=TEXT(stored=True, phrase=False),
        market_value=NUMERIC(stored=True),
        photoURL=ID(stored=True),
        team_logoURL=ID(stored=True),
        tags=KEYWORD(stored=True, commas=True),
    )

    if os.path.exists(TEAM_INDEX_DIR):
        shutil.rmtree(TEAM_INDEX_DIR)
    os.mkdir(TEAM_INDEX_DIR)

    if os.path.exists(PLAYER_INDEX_DIR):
        shutil.rmtree(PLAYER_INDEX_DIR)
    os.mkdir(PLAYER_INDEX_DIR)

    team_index = create_in(TEAM_INDEX_DIR, team_schema)
    player_index = create_in(PLAYER_INDEX_DIR, player_schema)

    team_writer = team_index.writer()
    player_writer = player_index.writer()

    for team in Team.objects.all():
        team_writer.add_document(
            id=str(team.id),
            name=team.name,
            market_value=team.market_value,
            average_age=team.average_age,
            foreigner_percentage=team.foreigner_percentage,
            goalkeepers=team.goalkeepers,
            defenders=team.defenders,
            midfielders=team.midfielders,
            forwards=team.forwards,
            logoURL=team.logoURL,
            tags=",".join([tag.name for tag in team.tags.all()]),
        )

    for player in Player.objects.all():
        player_writer.add_document(
            id=str(player.id),
            name=player.name,
            team=player.team.name,
            age=player.age,
            nationality=player.nationality,
            position=player.position,
            market_value=player.market_value,
            photoURL=player.photoURL,
            team_logoURL=player.team.logoURL,
            tags=",".join([tag.name for tag in player.tags.all()]),
        )

    team_writer.commit()
    player_writer.commit()


def list_teams():
    team_index = open_dir(TEAM_INDEX_DIR)
    with team_index.searcher() as searcher:
        team_list = []
        for team in searcher.documents():
            team_list.append(team)
        return team_list


def list_players():
    player_index = open_dir(PLAYER_INDEX_DIR)
    with player_index.searcher() as searcher:
        player_list = []
        for player in searcher.documents():
            player_list.append(player)
        return player_list


def teams_by_position_needed_and_max_average_age(position, max_age):
    team_index = open_dir(TEAM_INDEX_DIR)
    with team_index.searcher() as searcher:
        parser = QueryParser("tags", team_index.schema)
        position_query = parser.parse(position)

        max_age_query = NumericRange("average_age", 0, max_age)

        results = searcher.search(position_query & max_age_query, limit=None)

        team_list = []
        for team in Team.objects.all():
            if (
                team.name in [result["name"] for result in results]
                and team.average_age <= max_age
            ):
                team_list.append(team)

        return team_list


def players_by_team_and_value(team, min_value, max_value):
    player_index = open_dir(PLAYER_INDEX_DIR)
    with player_index.searcher() as searcher:
        parser = QueryParser("team", player_index.schema)
        team_query = parser.parse(team.name)

        min_value_query = NumericRange("market_value", min_value, None)
        max_value_query = NumericRange("market_value", None, max_value)

        results = searcher.search(
            team_query & min_value_query & max_value_query, limit=None
        )

        player_list = []
        for player in Player.objects.all():
            if (
                str(player.id) in [result["id"] for result in results]
                and player.name in [result["name"] for result in results]
                and (
                    player.market_value >= min_value
                    and player.market_value <= max_value
                )
            ):
                player_list.append(player)

        return player_list


def players_by_name_or_nationality(phrase):
    player_index = open_dir(PLAYER_INDEX_DIR)
    with player_index.searcher() as searcher:
        query = MultifieldParser(["name", "nationality"], player_index.schema).parse(
            '"' + phrase + '"'
        )

        results = searcher.search(query, limit=5)

        player_list = []
        for player in Player.objects.all():
            if str(player.id) in [
                result["id"] for result in results
            ] and player.name in [result["name"] for result in results]:
                player_list.append(player)

        return player_list


def update_position(player_id, position):
    original_player = Player.objects.get(id=player_id)
    original_position = original_player.position
    player_index = open_dir(PLAYER_INDEX_DIR)
    with player_index.searcher() as searcher:
        query = QueryParser("id", player_index.schema).parse(str(original_player.id))

        results = searcher.search(query, limit=1)

        if len(results) > 0:
            player_in_DB = Player.objects.get(id=original_player.id)
            player_in_DB.position = position
            player_in_DB.save()

            update_team_positions_and_tags(
                player_in_DB.team, original_position, player_in_DB.position
            )

            writer = player_index.writer()
            for r in results:
                writer.update_document(
                    id=str(original_player.id),
                    name=r["name"],
                    team=r["team"],
                    age=r["age"],
                    nationality=r["nationality"],
                    position=position,
                    market_value=r["market_value"],
                    photoURL=r["photoURL"],
                    team_logoURL=r["team_logoURL"],
                    tags=",".join([tag.name for tag in player_in_DB.tags.all()]),
                )
            writer.commit()

            return player_in_DB


def update_team_positions_and_tags(team, original_position, new_position):
    goalkeepers_diff = 0
    defenders_diff = 0
    midfielders_diff = 0
    forwards_diff = 0

    team_in_DB = Team.objects.get(name=team.name)
    if original_position == "Portero":
        team_in_DB.goalkeepers -= 1
        goalkeepers_diff -= 1
    elif original_position == "Defensa":
        team_in_DB.defenders -= 1
        defenders_diff -= 1
    elif original_position == "Centrocampista":
        team_in_DB.midfielders -= 1
        midfielders_diff -= 1
    elif original_position == "Delantero":
        team_in_DB.forwards -= 1
        forwards_diff -= 1

    if new_position == "Portero":
        team_in_DB.goalkeepers += 1
        goalkeepers_diff += 1
    elif new_position == "Defensa":
        team_in_DB.defenders += 1
        defenders_diff += 1
    elif new_position == "Centrocampista":
        team_in_DB.midfielders += 1
        midfielders_diff += 1
    elif new_position == "Delantero":
        team_in_DB.forwards += 1
        forwards_diff += 1

    team_in_DB.save()

    Tag.objects.all().delete()
    populate_tags()
    set_tags()

    team_index = open_dir(TEAM_INDEX_DIR)
    with team_index.searcher() as searcher:
        query = QueryParser("name", team_index.schema).parse(team.name)

        results = searcher.search(query, limit=1)

        if len(results) > 0:
            writer = team_index.writer()
            for r in results:
                writer.update_document(
                    id=str(team.id),
                    name=r["name"],
                    market_value=r["market_value"],
                    average_age=r["average_age"],
                    foreigner_percentage=r["foreigner_percentage"],
                    goalkeepers=r["goalkeepers"] + goalkeepers_diff,
                    defenders=r["defenders"] + defenders_diff,
                    midfielders=r["midfielders"] + midfielders_diff,
                    forwards=r["forwards"] + forwards_diff,
                    logoURL=r["logoURL"],
                    tags=",".join([tag.name for tag in team.tags.all()]),
                )
            writer.commit()
