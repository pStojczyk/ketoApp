import requests
from django.conf import settings

API_ID = getattr(settings, 'API_ID', '')
API_KEY = getattr(settings, 'API_KEY', '')
API_URL = getattr(settings, 'API_URL', '')


class GetConnection:
    def __init__(self, product, grams):
        self.product = product
        self.grams = grams

    def get_connection(self):
        print(API_ID, API_KEY, API_URL)
        api_url = f"https://api.edamam.com/api/nutrition-data?app_id={API_ID}&app_key=%20{API_KEY}&ingr={self.product}%20{self.grams}%20grams"
        result = requests.get(api_url)
        return result.json()


