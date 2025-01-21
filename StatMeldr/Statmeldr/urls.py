"""
URL configuration for Statmeldr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from api import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_cbs_data, name='get_cbs_data'),
    path('rivm/', views.get_rivm_data, name='get_rivm_data'),
    path('cbs/', views.get_cbs_data, name='get_cbs_data'),
    path('download_csv/', views.get_filtered_data_csv, name='get_filtered_data_csv'),
]
