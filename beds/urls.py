from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patient_reg/', views.patient_reg, name='patient_reg'),
    path('bedallocate/', views.bedallocate, name='bedallocate'),
    path('discharge/<int:id>', views.discharge, name='discharge'),
]
