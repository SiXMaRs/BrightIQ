from django.contrib import admin
from django.urls import path,include
from sklearnapp import views
urlpatterns = [
    # path('', views.home, name="sk-home")
    path('', views.HomeListView.as_view(), name="sk-home")
]
