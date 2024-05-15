from django.urls import path
from django.contrib.auth import views as auth_views
from .views import DemandDetailView, KetoAppUserUpdateView, Profile, Register
from .models import KetoAppUser


urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('ketoappuser-update/<int:pk>', KetoAppUserUpdateView.as_view(), name='keto_app_user_update'),
    # path('demand-detail', demand_detail, name='keto_app_user_demand_detail'),
    path('demand/<int:pk>', DemandDetailView.as_view(), name='keto_app_user_demand_detail'),
    path('profile/', Profile.as_view(), name='profile'),
]