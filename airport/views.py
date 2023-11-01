from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from airport.models import (
    AirplaneType,
    Airplane,
    Crew,
    Airport,
    Route,
    Flight,
    Order
)
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    AirportSerializer,
    RouteSerializer,
    FlightSerializer,
    OrderSerializer,
    AirplaneRetrieveSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    OrderRetrieveSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer

        return AirplaneSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        distance = self.request.query_params.get("distance")
    
        queryset = self.queryset
    
        if source:
            queryset = queryset.filter(source__name__icontains=source)
    
        if destination:
            queryset = queryset.filter(destination__name__icontains=destination)
    
        if distance:
            queryset = queryset.filter(distance=distance)
    
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteRetrieveSerializer

        return RouteSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects
        .prefetch_related("crew", "airplane", "route")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer

    def get_queryset(self):
        departure = self.request.query_params.get("departure_date")
        arrival = self.request.query_params.get("arrival_date")
        flight_id = self.request.query_params.get("flight")

        queryset = self.queryset

        if departure:
            queryset = queryset.filter(departure_time__date=departure)

        if arrival:
            queryset = queryset.filter(arrival_time__date=arrival)

        if flight_id:
            queryset = queryset.filter(flight__id=int(flight_id))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightRetrieveSerializer

        return FlightSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderRetrieveSerializer

        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "tickets__flight__crew",
            "tickets__flight__airplane",
            "tickets__flight__route__source",
            "tickets__flight__route__destination"
        )

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)
