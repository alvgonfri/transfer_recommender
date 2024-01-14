from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Player, Team


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class PlayerForm(forms.Form):
    players = Player.objects.all()

    player = forms.ModelChoiceField(
        queryset=players,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Selecciona un jugador",
    )


class TeamForm(forms.Form):
    teams = Team.objects.all()

    team = forms.ModelChoiceField(
        queryset=teams,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Selecciona un equipo",
    )


class PositionNeededAndMaxAverageAgeForm(forms.Form):
    positions = [
        ("", "Cualquiera"),
        ("Portero", "Portero"),
        ("Defensa", "Defensa"),
        ("Centrocampista", "Centrocampista"),
        ("Delantero", "Delantero"),
    ]

    position = forms.ChoiceField(
        choices=positions,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Posición",
    )

    max_age = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        label="Edad máxima",
    )


class TeamAndValueForm(forms.Form):
    teams = Team.objects.all()

    team = forms.ModelChoiceField(
        queryset=teams,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Selecciona un equipo",
    )

    min_value = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        label="Valor mínimo (mill. €)",
    )

    max_value = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        label="Valor máximo (mill. €)",
    )


class PhraseForm(forms.Form):
    phrase = forms.CharField(
        label="Frase",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class PlayerAndPositionForm(forms.Form):
    positions = [
        ("Portero", "Portero"),
        ("Defensa", "Defensa"),
        ("Centrocampista", "Centrocampista"),
        ("Delantero", "Delantero"),
    ]

    position = forms.ChoiceField(
        choices=positions,
        widget=forms.Select(attrs={"class": "form-control mb-4"}),
        label="Nueva posición",
    )

    def __init__(self, *args, **kwargs):
        super(PlayerAndPositionForm, self).__init__(*args, **kwargs)

        # Obtener la lista de jugadores
        players = Player.objects.all()

        # Crear una lista de opciones modificadas con la información adicional
        player_choices = [
            (
                player.id,
                f"{player.name} - {player.position} - {player.team}",
            )
            for player in players
        ]

        # Asignar las opciones modificadas al campo player
        self.fields["player"] = forms.ChoiceField(
            choices=[("", "Selecciona un jugador")] + player_choices,
            widget=forms.Select(attrs={"class": "form-control mb-4"}),
            label="Selecciona un jugador",
        )
