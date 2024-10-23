from django.urls import path
from .views import (AllEventsView, CalendarView, ProductDeleteView, ProductDetailView, ProductListByDateView,
                    ProductMacroNutrientsCreate, ProductMacroNutrientsUpdate, SendReportPdfView, SummaryView)

urlpatterns = [
    path('product/new/', ProductMacroNutrientsCreate.as_view(), name='product_create'),
    path('product/update/<int:pk>/', ProductMacroNutrientsUpdate.as_view(), name='product_update'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('list/<str:date>/', ProductListByDateView.as_view(), name='products_list_by_date'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('summary/<int:pk>/', SummaryView.as_view(), name='summary'),
    path('all_events/', AllEventsView.as_view(), name='all_events'),
    path('send-report-pdf/', SendReportPdfView.as_view(), name='send_report_pdf'),


]
