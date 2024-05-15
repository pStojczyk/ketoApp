from django.contrib import admin
from .models import Demand, KetoAppUser


admin.site.register(KetoAppUser)
admin.site.register(Demand)
