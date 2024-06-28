from django.urls import path
from .views import (Calendar2View, CalendarView, ProductDeleteView, ProductDetailView, ProductListByDateView,
                    ProductMacroNutrientsCreate, ProductMacroNutrientsUpdate, SummaryView, all_events)

urlpatterns = [
    path('product/new/', ProductMacroNutrientsCreate.as_view(), name='product_create'),
    path('product/update/<int:pk>/', ProductMacroNutrientsUpdate.as_view(), name='product_update'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('list/<str:date>/', ProductListByDateView.as_view(), name='products_list_by_date'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('summary/<int:pk>/', SummaryView.as_view(), name='summary'),
    path('calendar2/', Calendar2View.as_view(), name='calendar2'),
    path('all_events/', all_events, name='all_events'),
]
