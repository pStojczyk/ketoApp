"""
This module contains view classes for managing various user-related functionalities
in the application, including product management, personal user parameters,
and dietary demand information.
"""
from django.http import Http404

from rest_framework import mixins, status, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from calculator.models import FullDayIntake, Product
from users.models import Demand, KetoAppUser

from .serializers import DemandSerializer, FullDayIntakeSerializer,  ParameterSerializer, ProductSerializer


class ProductViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    A ViewSet for managing user-specific products, including creating, retrieving,
    updating, deleting, and listing products. Supports filtering and sorting.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self):
        """
        Filters and sorts the queryset based on query parameters.
        """
        queryset = super().get_queryset()
        name_filter = self.request.query_params.get('name', None)
        date_filter = self.request.query_params.get('date', None)
        ordering = self.request.query_params.get('ordering', None)

        if name_filter:
            queryset = queryset.filter(name=name_filter)
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        if ordering:
            valid_fields = ['name', '-name', 'date', '-date']
            if ordering in valid_fields:
                queryset = queryset.order_by(ordering)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new product for the authenticated user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(
            self.get_serializer(product).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """
        Updates an existing product's macronutrient data based on new weight (grams).
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_product = serializer.save()
        return Response(
            self.get_serializer(updated_product).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a product by its primary key (pk).
        """
        instance = self.get_object()
        instance.delete()

        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class PersonalParametersViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet for managing KetoAppUser personal parameters.
    Allows retrieving and updating user information such as weight, height,
    age, gender, and activity level.
    """
    serializer_class = ParameterSerializer

    def get_queryset(self):
        """
        Always return the queryset for the authenticated user's parameters.
        """
        user = self.request.user
        queryset = KetoAppUser.objects.filter(user=user)
        return queryset

    def get_object(self):
        """
        Always return the authenticated user's parameters.
        """
        return self.request.user.ketoappuser


class DemandDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ViewSet to retrieve a single Demand instance associated with the authenticated KetoAppUser.
    Allows the user to access their specific dietary demand information.
    """
    serializer_class = DemandSerializer

    def get_queryset(self):
        """
        Restrict the queryset to only the Demand instance associated with the authenticated user.
        """
        user = self.request.user.ketoappuser
        return Demand.objects.filter(keto_app_user=user)

    def get_object(self):
        """
        Retrieve the Demand instance for the currently authenticated user.
        Raise Http404 if not found.
        """
        queryset = self.get_queryset()
        try:
            return queryset.get()
        except Demand.DoesNotExist:
            raise Http404("Demand not found.")


class AllEventsAPIView(APIView):
    """
    API endpoint for retrieving all `FullDayIntake` instances for the logged-in user in JSON format.
    """

    def get(self, request):
        """
        Retrieves and formats all `FullDayIntake` instances for the logged-in user
        into a JSON response.

        Returns:
           A DRF object containing a list of events, each with:
                - 'title' (str): A summary of total calories, fat, protein, and carbohydrates.
                - 'start' (date): The date of the intake event.
                - 'url' (str): URL linking to the list of products for that date.
        """
        user = request.user.ketoappuser
        events = FullDayIntake.objects.filter(user=user)

        serializer = FullDayIntakeSerializer(events, many=True)

        return Response(serializer.data)