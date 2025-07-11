from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics, filters
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login as django_login
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from review_app.models import FoodPlace
from api.serializers import FoodPlaceSerializer
from django.shortcuts import get_object_or_404

from review_app.models import (
    User,
    FoodPlace,
    FoodItem,
    FoodReview,
    Category,
    StatusModel,
)
from api.serializers import (
    FoodPlaceSerializer,
    FoodItemSerializer,
    FoodReviewSerializer,
    CategorySerializer,
    RegisterUserSerializer,
    LoginSerializer,
)
from .paginators import CostumPagination


class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Selamat anda telah terdaftar...",
                    "data": serializer.data,
                }
            )
        return Response(
            {
                "status": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors,
            }
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        return JsonResponse(
            {
                "status": 200,
                "message": "Selamat anda berhasil masuk...",
                "data": {
                    "token": token.key,
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_reviewer": user.is_reviewer,
                },
            }
        )


class FoodPlaceListApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        places = FoodPlace.objects.all()
        serializer = FoodPlaceSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FoodPlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Tempat makan berhasil ditambahkan.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Data tidak valid.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class FoodPlaceDetailApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return FoodPlace.objects.get(pk=pk)
        except FoodPlace.DoesNotExist:
            return None

    def get(self, request, pk):
        place = self.get_object(pk)
        if not place:
            return Response({"message": "Tempat makan tidak ditemukan."}, status=404)
        serializer = FoodPlaceSerializer(place)
        return Response(serializer.data)

    def put(self, request, pk):
        place = self.get_object(pk)
        if not place:
            return Response({"message": "Tempat makan tidak ditemukan."}, status=404)

        serializer = FoodPlaceSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": 200,
                    "message": "Tempat makan berhasil diperbarui.",
                    "data": serializer.data,
                }
            )
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        place = self.get_object(pk)
        if not place:
            return Response({"message": "Tempat makan tidak ditemukan."}, status=404)
        place.delete()
        return Response(
            {"status": 200, "message": "Tempat makan berhasil dihapus."},
            status=status.HTTP_200_OK,
        )


class FoodItemListApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_status = StatusModel.objects.first()
        items = FoodItem.objects.select_related("place", "category").filter(
            status=active_status
        )
        serializer = FoodItemSerializer(items, many=True)
        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Data makanan berhasil dibaca.",
                "data": serializer.data,
            }
        )

    def post(self, request):
        serializer = FoodItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Data makanan berhasil ditambahkan.",
                    "data": serializer.data,
                }
            )
        return Response(
            {
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Validasi gagal.",
                "errors": serializer.errors,
            }
        )


class FoodItemDetailApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return FoodItem.objects.get(pk=pk)
        except FoodItem.DoesNotExist:
            return None

    def get(self, request, pk):
        food = self.get_object(pk)
        if not food:
            return Response(
                {"message": "Data tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = FoodItemSerializer(food)
        return Response(serializer.data)

    def put(self, request, pk):
        food = self.get_object(pk)
        if not food:
            return Response(
                {"message": "Data tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = FoodItemSerializer(food, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Data makanan berhasil diperbarui.",
                    "data": serializer.data,
                }
            )
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "errors": serializer.errors}
        )

    def delete(self, request, pk):
        food = self.get_object(pk)
        if not food:
            return Response(
                {"message": "Data tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND
            )
        food.delete()
        return Response(
            {"status": 200, "message": "Data makanan berhasil dihapus."},
            status=status.HTTP_200_OK,
        )


class FoodItemFilterApi(generics.ListAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    pagination_class = CostumPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["category__name"]
    ordering_fields = ["created_on", "price"]


class FoodReviewApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reviews = FoodReview.objects.select_related("food", "reviewer").all()
        serializer = FoodReviewSerializer(reviews, many=True)
        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Review berhasil diambil",
                "data": serializer.data,
            }
        )

    def post(self, request):
        serializer = FoodReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Review berhasil ditambahkan",
                    "data": serializer.data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
