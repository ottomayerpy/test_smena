from django.urls import path

from . import views

urlpatterns = [
    path('check/', views.CheckViews.as_view()),
    path('new_checks/', views.NewChecksViews.as_view()),
    path('create_checks/', views.CreateChecksViews.as_view()),
]
