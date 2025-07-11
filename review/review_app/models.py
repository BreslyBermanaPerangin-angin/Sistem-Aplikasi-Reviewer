import sys
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


class User(AbstractUser):
    is_reviewer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} {self.first_name} {self.last_name}"

class StatusModel(models.Model):
    status_choices = (
        ("Aktif", "Aktif"),
        ("Tidak Aktif", "Tidak Aktif"),
    )

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=status_choices, default="Aktif")
    user_create = models.ForeignKey(User, related_name="user_create_status", blank=True, null=True, on_delete=models.SET_NULL)
    user_update = models.ForeignKey(User, related_name="user_update_status", blank=True, null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class FoodPlace(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255)
    status = models.ForeignKey(StatusModel, related_name="status_foodplace", on_delete=models.PROTECT)
    user_create = models.ForeignKey(User, related_name="user_create_foodplace", blank=True, null=True, on_delete=models.SET_NULL)
    user_update = models.ForeignKey(User, related_name="user_update_foodplace", blank=True, null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    status = models.ForeignKey(StatusModel, related_name="status_category", on_delete=models.PROTECT)
    user_create = models.ForeignKey(User, related_name="user_create_category", blank=True, null=True, on_delete=models.SET_NULL)
    user_update = models.ForeignKey(User, related_name="user_update_category", blank=True, null=True, on_delete=models.SET_NULL)
    create_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

def compress_image(image, filename):
    curr_datetime = datetime.now().strftime('%Y%m%d %H%M%S')
    im = Image.open(image)
    if im.mode != 'RGB':
        im = im.convert('RGB')
    im_io = BytesIO()
    im.save(im_io, 'jpeg', quality=50, optimize=True)
    im.seek(0)
    new_image = InMemoryUploadedFile(im_io, 'ImageField', f'{filename}-{curr_datetime}.jpg', 'image/jpeg', sys.getsizeof(im_io), None)
    return new_image

def increment_food_code():
    last_code = FoodItem.objects.all().order_by('id').last()
    if not last_code:
        return 'FD-0001'
    code = last_code.code
    code_int = int(code[3:7])
    new_code_int = code_int + 1
    return 'FD-' + str(new_code_int).zfill(4)


class FoodItem(models.Model):
    code = models.CharField(max_length=20, default=increment_food_code, editable=False)
    place = models.ForeignKey(FoodPlace, related_name="foods", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='category_food', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.ForeignKey(StatusModel, related_name='status_food', on_delete=models.PROTECT)
    user_create = models.ForeignKey(User, related_name='user_create_food', blank=True, null=True, on_delete=models.SET_NULL)
    user_update = models.ForeignKey(User, related_name='user_update_food', blank=True, null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.place.name})"

    def save(self, *args, **kwargs):
        if self.id:
            try:
                old = FoodItem.objects.get(id=self.id)
                if old.image != self.image:
                    if self.image:
                        self.image = compress_image(self.image, 'food')
                        old.image.delete()
            except:
                pass
            super().save(*args, **kwargs)
        else:
            if self.image:
                self.image = compress_image(self.image, 'food')
            super().save(*args, **kwargs)


class FoodReview(models.Model):
    food = models.ForeignKey(FoodItem, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name="reviewer", on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    distance_km = models.FloatField(help_text="Jarak dari reviewer ke lokasi (dalam km)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.food.name} ({self.rating}/5)"