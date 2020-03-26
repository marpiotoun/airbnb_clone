from django.urls import path
from . import views


app_name = 'room'


urlpatterns = [
    path('<int:pk>', views.RoomDetail.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EditRoom.as_view(), name='edit'),
    path('<int:pk>/edit/photos', views.EditPhotosView.as_view(), name='edit-photos'),
    path('search/', views.search, name='search'),

]
# path('<int:pk>', views.room_detail, name='detail'),
