from django.urls import path
from . import views


app_name = 'room'


urlpatterns = [
    path('<int:pk>/', views.RoomDetail.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EditRoom.as_view(), name='edit'),
    path('create/', views.CreateRoomView.as_view(), name='create'),
    path('<int:pk>/edit/photos/', views.EditPhotosView.as_view(), name='edit-photos'),
    path('<int:pk>/edit/photos/add/', views.AddPhotoView.as_view(), name='add-photos'),
    path('<int:room_pk>/edit/photos/<int:photo_pk>/update/', views.UpdatePhotoView.as_view(), name='update-photo'),
    path('<int:room_pk>/edit/photos/<int:photo_pk>/delete/', views.delete_photo, name='delete-photos'),
    path('search/', views.search, name='search'),
]
# path('<int:pk>', views.room_detail, name='detail'),
