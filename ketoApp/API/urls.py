from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AllEventsAPIView, DemandDetailViewSet, PersonalParametersViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'personal-parameters', PersonalParametersViewSet, basename='personal-parameters')
router.register(r'demand', DemandDetailViewSet, basename='demand')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/all-events/', AllEventsAPIView.as_view(), name='all-events'),
]

