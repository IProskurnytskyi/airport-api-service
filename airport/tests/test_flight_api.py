from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Flight,
    Airport,
    Route,
    Airplane,
    Crew,
    AirplaneType,
    Ticket,
    Order,
)
from airport.serializers import (
    FlightListSerializer,
    FlightRetrieveSerializer
)

FLIGHT_URL = reverse("airport:flight-list")


def create_flight(
    source_airport_name="Airport A",
    destination_airport_name="Airport B",
    airplane_name="Airplane C",
    departure_time="2023-11-01T08:00:00Z",
    arrival_time="2023-11-01T10:00:00Z",
) -> Flight:
    source_airport = Airport.objects.create(
        name=source_airport_name, closest_big_city="City A"
    )
    destination_airport = Airport.objects.create(
        name=destination_airport_name, closest_big_city="City B"
    )
    route = Route.objects.create(
        source=source_airport,
        destination=destination_airport,
        distance=100
    )
    airplane_type = AirplaneType.objects.create(name="Type A")
    airplane = Airplane.objects.create(
        name=airplane_name,
        rows=10,
        seats_in_row=6,
        airplane_type=airplane_type
    )
    crew_member = Crew.objects.create(first_name="Bob", last_name="Core")
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=departure_time,
        arrival_time=arrival_time
    )
    flight.crew.add(crew_member)
    return flight


def flight_detail_url(flight_id: int):
    return reverse("airport:flight-detail", args=[flight_id])


def remove_tickets_available(data: list[dict]) -> None:
    for instance in data:
        instance.pop("tickets_available")


def get_payload() -> dict:
    airplane_type = AirplaneType.objects.create(name="Type Y")
    airplane = Airplane.objects.create(
        name="Airplane Z", rows=8, seats_in_row=6, airplane_type=airplane_type
    )
    source_airport = Airport.objects.create(
        name="Airport A",
        closest_big_city="City A"
    )
    destination_airport = Airport.objects.create(
        name="Airport B",
        closest_big_city="City B"
    )
    route = Route.objects.create(
        source=source_airport, destination=destination_airport, distance=100
    )
    crew_member = Crew.objects.create(first_name="Bob", last_name="Core")
    return {
        "route": route.id,
        "airplane": airplane.id,
        "departure_time": "2023-11-01T08:00:00Z",
        "arrival_time": "2023-11-01T10:00:00Z",
        "crew": [crew_member.id],
    }


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_flights(self) -> None:
        create_flight()
        create_flight(
            source_airport_name="Airport D",
            destination_airport_name="Airport F",
            airplane_name="Airplane G",
        )

        response = self.client.get(FLIGHT_URL)

        remove_tickets_available(response.data)

        flights = Flight.objects.order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_flights_by_departure_date(self) -> None:
        flight_1 = create_flight(departure_time="2023-11-01T08:00:00Z")
        flight_2 = create_flight(departure_time="2023-11-02T08:00:00Z")

        response = self.client.get(
            FLIGHT_URL, {"departure_date": "2023-11-01"}
        )

        remove_tickets_available(response.data)

        serializer_1 = FlightListSerializer(flight_1)
        serializer_2 = FlightListSerializer(flight_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(serializer_1.data, response.data)
        self.assertNotIn(serializer_2.data, response.data)

    def test_filter_flights_by_arrival_date(self) -> None:
        flight_1 = create_flight(arrival_time="2023-11-01T10:00:00Z")
        flight_2 = create_flight(arrival_time="2023-11-02T10:00:00Z")

        response = self.client.get(FLIGHT_URL, {"arrival_date": "2023-11-02"})

        remove_tickets_available(response.data)

        serializer_1 = FlightListSerializer(flight_1)
        serializer_2 = FlightListSerializer(flight_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertNotIn(serializer_1.data, response.data)
        self.assertIn(serializer_2.data, response.data)

    def test_filter_flights_by_flight_id(self) -> None:
        flight_1 = create_flight()
        flight_2 = create_flight(
            source_airport_name="Airport K",
            destination_airport_name="Airport L",
            airplane_name="Airplane Y",
        )

        response = self.client.get(FLIGHT_URL, {"flight": flight_1.id})

        remove_tickets_available(response.data)

        serializer_1 = FlightListSerializer(flight_1)
        serializer_2 = FlightListSerializer(flight_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(serializer_1.data, response.data)
        self.assertNotIn(serializer_2.data, response.data)

    def test_retrieve_flight_detail(self) -> None:
        flight = create_flight()
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(row=1, seat=1, flight=flight, order=order)
        Ticket.objects.create(row=2, seat=2, flight=flight, order=order)

        response = self.client.get(flight_detail_url(flight.id))

        serializer = FlightRetrieveSerializer(flight)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], flight.id)
        self.assertEqual(len(response.data["taken_places"]), 2)
        self.assertEqual(response.data, serializer.data)

    def test_create_flight_forbidden(self) -> None:
        payload = get_payload()

        response = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_flight_forbidden(self) -> None:
        payload = get_payload()

        flight = create_flight()
        url = flight_detail_url(flight.id)

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_flight_forbidden(self) -> None:
        flight = create_flight()
        url = flight_detail_url(flight.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self) -> None:
        payload = get_payload()
        
        response = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_flight(self) -> None:
        payload = get_payload()

        flight = create_flight()
        url = flight_detail_url(flight.id)

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_flight(self) -> None:
        flight = create_flight()
        url = flight_detail_url(flight.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
