from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    market_value = models.FloatField()
    average_age = models.FloatField()
    foreigner_percentage = models.FloatField()
    goalkeepers = models.IntegerField()
    defenders = models.IntegerField()
    midfielders = models.IntegerField()
    forwards = models.IntegerField()
    logoURL = models.CharField(max_length=200)

    tags = models.ManyToManyField(Tag)

    def get_needed_positions(self):
        needed_positions = []

        if self.goalkeepers <= 2:
            needed_positions.append("Portero")
        if self.defenders <= 7:
            needed_positions.append("Defensa")
        if self.midfielders <= 7:
            needed_positions.append("Centrocampista")
        if self.forwards <= 5:
            needed_positions.append("Delantero")

        return needed_positions

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    age = models.IntegerField()
    nationality = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    market_value = models.FloatField()
    photoURL = models.CharField(max_length=200)

    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name
