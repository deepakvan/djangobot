
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page),
    path('start_bot/', views.start_bot),
    path('stop_bot/',views.update_model_on_startup),
]
