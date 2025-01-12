"""
This module contains serializers for the `Product`, `KetoAppUser`, and `Demand` models
used in the application. Serializers are responsible for converting complex data types,
such as model instances, into JSON format and vice versa. They facilitate the validation
and transformation of input data from API requests.
"""
from datetime import date

from django.urls import reverse_lazy
from rest_framework import serializers

from calculator.models import FullDayIntake, Product
from calculator.utils import GetConnection
from users.models import Demand, KetoAppUser


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    This serializer is responsible for serializing and deserializing
    product data, allowing for the creation and updating of Product
    instances. It retrieves nutritional information from an external API
    based on the product name and grams provided.

    Attributes:
        product_name (str): The name of the product, required for creation.
        grams (float): The weight of the product in grams, required for creation.
    """

    id = serializers.CharField(read_only=True)
    kcal = serializers.FloatField(read_only=True)
    carb = serializers.FloatField(read_only=True)
    fat = serializers.FloatField(read_only=True)
    protein = serializers.FloatField(read_only=True)
    date = serializers.DateField(read_only=True, format="%Y-%m-%d")

    class Meta:
        model = Product
        fields = ['id', 'name', 'grams', 'kcal', 'carb', 'fat', 'protein', 'date']

    def create(self, validated_data):
        """
        Creates a new Product instance using the validated data.
        This method extracts the `product_name` and `grams` from the validated data,
        fetches nutritional information from an external API based on the provided
        product name and grams, and then creates a new Product instance in the
        database.
        """

        product_name = validated_data.get('name')
        grams = validated_data.pop('grams')

        product_request = GetConnection(product_name, grams).get_connection()

        product = Product.objects.create(
            name=product_name,
            grams=grams,
            kcal=product_request['calories'],
            carb=product_request['totalNutrients']['CHOCDF']['quantity'],
            fat=product_request['totalNutrients']['FAT']['quantity'],
            protein=product_request['totalNutrients']['PROCNT']['quantity'],
            date=validated_data.get('date', date.today())
        )
        return product

    def update(self, instance, validated_data):
        """
        Updates an existing Product instance with new data fetched from the external API.
        This method updates the product's grams and nutritional values using
        the external API based on the product's name.
        """
        grams = validated_data.get('grams', instance.grams)

        product_request = GetConnection(instance.name, grams).get_connection()

        instance.grams = grams
        instance.kcal = product_request['calories']
        instance.carb = product_request['totalNutrients']['CHOCDF']['quantity']
        instance.fat = product_request['totalNutrients']['FAT']['quantity']
        instance.protein = product_request['totalNutrients']['PROCNT']['quantity']

        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize the representation of the Product instance.
        This method adds a success message to the output when a product is created.
        """
        representation = super().to_representation(instance)
        representation['message'] = f"Product {instance.name} created successfully!"
        return representation


class ParameterSerializer(serializers.ModelSerializer):
    """
    Serializer for the KetoAppUser model parameters.
    This serializer is responsible for serializing and deserializing the parameters
    of the KetoAppUser model, allowing for the representation and manipulation
    of user-related data such as weight, height, age, gender, and activity level.
    """
    class Meta:
        model = KetoAppUser
        fields = ['id', 'weight', 'height', 'age', 'gender', 'activity']


class DemandSerializer(serializers.ModelSerializer):
    """
    Serializer for the Demand model.
    This serializer is used to convert Demand instances to and from JSON format.
    It handles the serialization and deserialization of the Demand model fields.
    """
    kcal = serializers.IntegerField(required=True)
    fat = serializers.IntegerField(required=True)
    protein = serializers.IntegerField(required=True)
    carbs = serializers.IntegerField(required=True)

    class Meta:
        model = Demand
        fields = ['id', 'keto_app_user', 'kcal', 'fat', 'protein', 'carbs']
        read_only_fields = ['keto_app_user']


class FullDayIntakeSerializer(serializers.ModelSerializer):
    """Serializer for FullDayIntake model."""

    title = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    class Meta:
        model = FullDayIntake
        fields = ['title', 'start', 'url', 'details']

    def get_title(self, obj):
        """Generate a title with total macronutrients for the event."""
        return (
            f'TOTAL KCAL: {obj.total_kcal}\n'
            f'TOTAL FAT: {obj.total_fat}\n'
            f'TOTAL PROTEIN: {obj.total_protein}\n'
            f'TOTAL CARBS: {obj.total_carbs}'
        )

    def get_start(self, obj):
        return obj.date.strftime("%Y-%m-%d")

    def get_url(self, obj):
        """Generate the URL linking to the list of products for that date."""
        return reverse_lazy('products_list_by_date', args=[obj.date])

    def get_details(self, obj):
        return f"Uwagi: {obj.remarks if hasattr(obj, 'remarks') else 'Brak dodatkowych informacji'}"

