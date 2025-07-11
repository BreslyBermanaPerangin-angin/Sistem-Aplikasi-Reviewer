from rest_framework import serializers
from review_app.models import (
    User, StatusModel, FoodPlace, Category, FoodItem, FoodReview
)
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# ======================
# SERIALIZER: FoodPlace
# ======================

class FoodPlaceSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(queryset=StatusModel.objects.all())

    class Meta:
        model = FoodPlace
        fields = ['id', 'name', 'description', 'latitude', 'longitude', 'address', 'status']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Ubah ID status menjadi string-nya
        rep['status'] = str(instance.status)
        return rep

# ======================
# SERIALIZER: Category
# ======================

class CategorySerializer(serializers.ModelSerializer):
    status = serializers.StringRelatedField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'status']

# ======================
# SERIALIZER: FoodItem
# ======================

class FoodItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    place = serializers.StringRelatedField()
    status = serializers.StringRelatedField()

    class Meta:
        model = FoodItem
        fields = ['id', 'code', 'name', 'price', 'description', 'image', 'category', 'place', 'status']

# ======================
# SERIALIZER: FoodReview
# ======================

class FoodReviewSerializer(serializers.ModelSerializer):
    food = serializers.StringRelatedField()
    reviewer = serializers.StringRelatedField()

    class Meta:
        model = FoodReview
        fields = ['id', 'food', 'reviewer', 'rating', 'comment', 'distance_km', 'created_at']

# ======================
# SERIALIZER: Register User
# ======================

class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_active', 'is_reviewer', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Kata sandi dan ulangi kata sandi tidak sama'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=validated_data['is_active'],
            is_reviewer=validated_data['is_reviewer'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user

# ======================
# SERIALIZER: Login
# ======================

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username', '')
        password = data.get('password', '')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active and user.is_reviewer:
                    data['user'] = user
                else:
                    raise ValidationError({'message': 'Akun tidak aktif atau bukan reviewer.'})
            else:
                raise ValidationError({'message': 'Username atau password salah.'})
        else:
            raise ValidationError({'message': 'Mohon lengkapi username dan password.'})
        return data
