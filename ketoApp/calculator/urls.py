from django.urls import path
from .views import (CalendarView, ProductDeleteView, ProductDetailView, ProductListByDateView,
                    ProductMacroNutrientsCreate, ProductMacroNutrientsUpdate, SummaryDetailView)


urlpatterns = [
    path('product/new/', ProductMacroNutrientsCreate.as_view(), name='product_create'),
    path('product/update/<int:pk>/', ProductMacroNutrientsUpdate.as_view(), name='product_update'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('list/<str:date>/', ProductListByDateView.as_view(), name='products_list_by_date'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('summary/<int:pk>/', SummaryDetailView.as_view(), name='full_day_macronutrients'),
    # path('summary/<int:pk>', sum_all_products_nutrients, name='full_day_macronutrients'),



]
