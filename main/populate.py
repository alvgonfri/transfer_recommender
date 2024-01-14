from bs4 import BeautifulSoup
import requests
from main.models import Tag, Team, Player

PAGE = "https://www.transfermarkt.es/laliga/startseite/wettbewerb/ES1/saison_id/2023"

# Lines to avoid SSL error
import os, ssl

if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
    ssl, "_create_unverified_context", None
):
    ssl._create_default_https_context = ssl._create_unverified_context


def populate_database():
    delete_tables()
    teams_list, players_list = extract_data()
    populate_teams(teams_list)
    populate_players(players_list)
    populate_tags()
    set_tags()


def delete_tables():
    Tag.objects.all().delete()
    Team.objects.all().delete()
    Player.objects.all().delete()


def populate_teams(teams_list):
    for team in teams_list:
        t = Team(
            name=team[0],
            market_value=team[1],
            average_age=team[2],
            foreigner_percentage=team[3],
            goalkeepers=team[4],
            defenders=team[5],
            midfielders=team[6],
            forwards=team[7],
            logoURL=team[8],
        )
        t.save()


def populate_players(players_list):
    for player in players_list:
        p = Player(
            name=player[0],
            team=Team.objects.get(name=player[1]),
            age=player[2],
            nationality=player[3],
            position=player[4],
            market_value=player[5],
            photoURL=player[6],
        )
        p.save()


def populate_tags():
    tags = [
        "Local",
        "Extranjero",
        "Joven",
        "Experimentado",
        "Valor alto",
        "Valor medio",
        "Valor bajo",
        "Portero",
        "Defensa",
        "Centrocampista",
        "Delantero",
    ]
    for tag in tags:
        t = Tag(name=tag)
        t.save()


def set_tags():
    teams = Team.objects.all()
    players = Player.objects.all()

    for team in teams:
        if team.foreigner_percentage > 50:
            team.tags.add(Tag.objects.get(name="Extranjero"))
        else:
            team.tags.add(Tag.objects.get(name="Local"))

        if team.average_age >= 27:
            team.tags.add(Tag.objects.get(name="Experimentado"))
        else:
            team.tags.add(Tag.objects.get(name="Joven"))

        if team.market_value >= 400:
            team.tags.add(Tag.objects.get(name="Valor alto"))
        elif team.market_value >= 100:
            team.tags.add(Tag.objects.get(name="Valor medio"))
        else:
            team.tags.add(Tag.objects.get(name="Valor bajo"))

        needed_positions = team.get_needed_positions()
        for position in needed_positions:
            team.tags.add(Tag.objects.get(name=position))

        team.save()

    for player in players:
        if player.nationality != "España":
            player.tags.add(Tag.objects.get(name="Extranjero"))
        else:
            player.tags.add(Tag.objects.get(name="Local"))

        if player.age >= 23:
            player.tags.add(Tag.objects.get(name="Experimentado"))
        else:
            player.tags.add(Tag.objects.get(name="Joven"))

        if player.market_value >= 30:
            player.tags.add(Tag.objects.get(name="Valor alto"))
        elif player.market_value >= 10:
            player.tags.add(Tag.objects.get(name="Valor medio"))
        else:
            player.tags.add(Tag.objects.get(name="Valor bajo"))

        if player.position == "Portero":
            player.tags.add(Tag.objects.get(name="Portero"))
        elif player.position == "Defensa":
            player.tags.add(Tag.objects.get(name="Defensa"))
        elif player.position == "Centrocampista":
            player.tags.add(Tag.objects.get(name="Centrocampista"))
        else:
            player.tags.add(Tag.objects.get(name="Delantero"))

        player.save()


def extract_data():
    teams_list = []
    players_list = []

    url = PAGE
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    f = requests.get(url, headers=headers)
    s = BeautifulSoup(f.text, "lxml")
    teams = s.find("div", id="yw1").find_all("td", class_="hauptlink no-border-links")

    for team in teams:
        link = team.a["href"]
        f = requests.get("https://www.transfermarkt.es" + link, headers=headers)
        s = BeautifulSoup(f.text, "lxml")

        # Extract team name
        team_name = "Desconocido"
        if s.find(
            "h1",
            class_="data-header__headline-wrapper data-header__headline-wrapper--oswald",
        ):
            team_name = s.find(
                "h1",
                class_="data-header__headline-wrapper data-header__headline-wrapper--oswald",
            ).string.strip()

        # Extract team data (used to extract market value, average age and foreigner percentage)
        data = s.find("div", class_="data-header__details").find("ul")

        # Extract market value
        market_value = "Desconocido"
        if data.find("li").find_next_sibling("li").find_next_sibling("li").find("a"):
            unit = (
                s.find("div", class_="data-header__box--small")
                .find("a")
                .find("span")
                .string.strip()
            )
            market_value = float(
                s.find("div", class_="data-header__box--small")
                .find("a")
                .get_text()
                .split(" ")[0]
                .replace(",", ".")
            )
            if unit == "mil mill. €":
                market_value *= 1000

        # Extract average age
        avegare_age = "Desconocida"
        if data.find("li").find_next_sibling("li").find("span"):
            avegare_age = float(
                (
                    data.find("li")
                    .find_next_sibling("li")
                    .find("span")
                    .string.strip()
                    .replace(",", ".")
                )
            )

        # Extract foreigner percentage
        foreigner_percentage = "Desconocido"
        if (
            data.find("li")
            .find_next_sibling("li")
            .find_next_sibling("li")
            .find("span")
            .find("span")
        ):
            foreigner_percentage = float(
                (
                    data.find("li")
                    .find_next_sibling("li")
                    .find_next_sibling("li")
                    .find("span")
                    .find("span")
                    .string.strip()
                    .split(" ")[0]
                    .replace(",", ".")
                )
            )

        # Extract logo
        logo = "Desconocido"
        if s.find("div", class_="data-header__profile-container"):
            logo = (
                s.find("div", class_="data-header__profile-container")
                .find("img")["src"]
                .strip()
            )

        # Extract players
        players_odd = s.find("div", id="yw1").find("tbody").find_all("tr", class_="odd")
        players_even = (
            s.find("div", id="yw1").find("tbody").find_all("tr", class_="even")
        )
        players = players_odd + players_even

        # Initialize position counters
        goalkeepers = 0
        defenders = 0
        midfielders = 0
        forwards = 0

        for player in players:
            # Extract player name
            player_name = "Desconocido"
            if player.find("td", class_="hauptlink"):
                player_name = player.find("td", class_="hauptlink").get_text().strip()

            # Set player team
            player_team = team_name

            # Extract player age
            age = "Desconocida"
            if player.find("td", class_="posrela").find_next_sibling("td"):
                age = int(
                    player.find("td", class_="posrela")
                    .find_next_sibling("td")
                    .string.split(" ")[1]
                    .replace("(", "")
                    .replace(")", "")
                    .strip()
                )

            # Extract player nationality
            nationality = "Desconocida"
            if (
                player.find("td", class_="posrela")
                .find_next_sibling("td")
                .find_next_sibling("td")
            ):
                nationality = (
                    player.find("td", class_="posrela")
                    .find_next_sibling("td")
                    .find_next_sibling("td")
                    .find("img")["title"]
                )

            # Extract player position and update position counters
            position = "Desconocida"
            if player.find("td", class_="zentriert rueckennummer bg_Torwart"):
                goalkeepers += 1
                position = "Portero"
            elif player.find("td", class_="zentriert rueckennummer bg_Abwehr"):
                defenders += 1
                position = "Defensa"
            elif player.find("td", class_="zentriert rueckennummer bg_Mittelfeld"):
                midfielders += 1
                position = "Centrocampista"
            elif player.find("td", class_="zentriert rueckennummer bg_Sturm"):
                forwards += 1
                position = "Delantero"

            # Extract player market value
            player_market_value = "Desconocido"
            if player.find("td", class_="rechts hauptlink").find("a"):
                unit = (
                    player.find("td", class_="rechts hauptlink")
                    .find("a")
                    .string.split(" ")[1]
                    .strip()
                )
                player_market_value = float(
                    player.find("td", class_="rechts hauptlink")
                    .find("a")
                    .string.split(" ")[0]
                    .replace(",", ".")
                )
                if unit == "mil":
                    player_market_value /= 1000

            # Extract player photo
            player_photo = "Desconocida"
            if (
                player.find("td", class_="posrela")
                .find("table", class_="inline-table")
                .find("img")
            ):
                player_photo = (
                    player.find("td", class_="posrela")
                    .find("table", class_="inline-table")
                    .find("img")["data-src"]
                    .strip()
                )

            # Append player to players list
            players_list.append(
                (
                    player_name,
                    player_team,
                    age,
                    nationality,
                    position,
                    player_market_value,
                    player_photo,
                )
            )

        # Append team to teams list
        teams_list.append(
            (
                team_name,
                market_value,
                avegare_age,
                foreigner_percentage,
                goalkeepers,
                defenders,
                midfielders,
                forwards,
                logo,
            )
        )

    return teams_list, players_list
