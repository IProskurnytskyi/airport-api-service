from django.db import models

from airport_api_service import settings


class AirplaneType(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=128)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, null=True, on_delete=models.SET_NULL, related_name="airplanes"
    )

    def __str__(self) -> str:
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(max_length=128)
    closest_big_city = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="source_routs")
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routs"
    )
    distance = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.source}-{self.destination}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    def __str__(self) -> str:
        return f"{self.departure_time}-{self.arrival_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    def __str__(self) -> str:
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
