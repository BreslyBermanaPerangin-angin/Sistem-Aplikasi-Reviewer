from django.contrib import admin
from review_app.models import User, StatusModel, FoodPlace, Category, FoodItem, FoodReview

admin.site.register(User)
admin.site.register(StatusModel)
admin.site.register(FoodPlace)
admin.site.register(Category)
admin.site.register(FoodItem)
admin.site.register(FoodReview)
