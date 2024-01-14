import shelve
from .models import Team, Player


def load_similarities():
    shelf = shelve.open("dataRS.dat")
    shelf["similarities"] = compute_similarities()
    shelf["inverse_similarities"] = compute_inverse_similarities()
    shelf["player_similarities"] = compute_player_similarities()
    shelf["team_similarities"] = compute_team_similarities()
    shelf.close()


# This function computes the similarities between players and teams
def compute_similarities():
    res = {}
    team_tags = {}
    player_tags = {}

    for team in Team.objects.all():
        team_tags[team.name] = set([tag.name for tag in team.tags.all()])

    for player in Player.objects.all():
        player_tags[(player.pk, player.name)] = set(
            [tag.name for tag in player.tags.all()]
        )

    for player_tuple, player_tags_set in player_tags.items():
        top_teams = {}
        for team_name, team_tags_set in team_tags.items():
            # We don't want to recommend a player's own team
            if team_name != Player.objects.get(pk=player_tuple[0]).team.name:
                similarity_coefficient = dice_coefficient(
                    player_tags_set, team_tags_set
                )
                top_teams[team_name] = similarity_coefficient
        res[player_tuple] = sorted(top_teams.items(), key=lambda x: x[1], reverse=True)

    return res


# This function computes the similarities between teams and players
def compute_inverse_similarities():
    res = {}
    team_tags = {}
    player_tags = {}

    for team in Team.objects.all():
        team_tags[team.name] = set([tag.name for tag in team.tags.all()])

    for player in Player.objects.all():
        player_tags[(player.pk, player.name)] = set(
            [tag.name for tag in player.tags.all()]
        )

    for team_name, team_tags_set in team_tags.items():
        top_players = {}
        for player_tuple, player_tags_set in player_tags.items():
            # We don't want to recommend a team's own players
            if team_name != Player.objects.get(pk=player_tuple[0]).team.name:
                similarity_coefficient = dice_coefficient(
                    player_tags_set, team_tags_set
                )
                top_players[player_tuple] = similarity_coefficient
        res[team_name] = sorted(top_players.items(), key=lambda x: x[1], reverse=True)

    return res


# This function computes the similarities between teams
def compute_team_similarities():
    res = {}
    team_tags = {}

    for team in Team.objects.all():
        team_tags[team.name] = set([tag.name for tag in team.tags.all()])

    for team_name1, team_tags_set1 in team_tags.items():
        top_teams = {}
        for team_name2, team_tags_set2 in team_tags.items():
            # We only want to compare different teams
            if team_name1 != team_name2:
                similarity_coefficient = dice_coefficient(
                    team_tags_set1, team_tags_set2
                )
                top_teams[team_name2] = similarity_coefficient
        res[team_name1] = sorted(top_teams.items(), key=lambda x: x[1], reverse=True)

    return res


# This function computes the similarities between players
def compute_player_similarities():
    res = {}
    player_tags = {}

    for player in Player.objects.all():
        player_tags[(player.pk, player.name)] = set(
            [tag.name for tag in player.tags.all()]
        )

    for player_tuple1, player_tags_set1 in player_tags.items():
        top_players = {}
        for player_tuple2, player_tags_set2 in player_tags.items():
            # We only want to compare different players
            if player_tuple1[0] != player_tuple2[0]:
                similarity_coefficient = dice_coefficient(
                    player_tags_set1, player_tags_set2
                )
                top_players[player_tuple2] = similarity_coefficient
        res[player_tuple1] = sorted(
            top_players.items(), key=lambda x: x[1], reverse=True
        )

    return res


# This function computes the Dice coefficient between two sets
def dice_coefficient(set1, set2):
    return 2 * len(set1.intersection(set2)) / (len(set1) + len(set2))


# This function returns the top 3 teams for a given player
def recommend_teams(player):
    shelf = shelve.open("dataRS.dat")
    similarities = shelf["similarities"]
    shelf.close()
    return similarities[(player.pk, player.name)][:3]


# This function returns the top 10 players for a given team
def recommend_players(team):
    shelf = shelve.open("dataRS.dat")
    inverse_similarities = shelf["inverse_similarities"]
    shelf.close()
    return inverse_similarities[team.name][:10]


# This function returns the top 5 similar players for a given player
def similar_players(player):
    shelf = shelve.open("dataRS.dat")
    player_similarities = shelf["player_similarities"]
    shelf.close()
    return player_similarities[(player.pk, player.name)][:5]


# This function returns the top 3 similar teams for a given team
def similar_teams(team):
    shelf = shelve.open("dataRS.dat")
    team_similarities = shelf["team_similarities"]
    shelf.close()
    return team_similarities[team.name][:3]
