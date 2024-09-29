from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/', include('users.urls') ),
    path('api/metdata/', include('metdata.urls') ),
    path('api/geoglows/', include('geoglows.urls') ),
    ###############################################
    path('api/national-waterlevel-forecast/', include('app_national_waterlevel_forecast.urls')),
]
