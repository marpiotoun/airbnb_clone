from django.urls import path
from . import views


app_name = 'review'

urlpatterns = [
    path('create/<int:room>', views.create_review, name='create')
]