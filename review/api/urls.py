from django.urls import path
from .views import (
    RegisterUserAPIView, LoginView,
    FoodPlaceListApiView,
    FoodItemListApiView, FoodItemDetailApiView,
    FoodItemFilterApi, FoodReviewApiView, FoodPlaceDetailApiView,
    UserViewSet
)
from rest_framework.routers import DefaultRouter

app_name = 'api'

urlpatterns = [
    path('api/register/', RegisterUserAPIView.as_view()),
    path('api/login/', LoginView.as_view()),
    path('api/places/', FoodPlaceListApiView.as_view()),
    path('api/places/<int:pk>/', FoodPlaceDetailApiView.as_view()),
    path('api/foods/', FoodItemListApiView.as_view()),
    path('api/foods/<int:pk>/', FoodItemDetailApiView.as_view()),
    path('api/foods/filter/', FoodItemFilterApi.as_view()),
    path('api/reviews/', FoodReviewApiView.as_view()),
    path('api/reviews/<int:pk>/', FoodReviewApiView.as_view()),
]

router = DefaultRouter()
router.register(r'users', UserViewSet)
urlpatterns += router.urls
