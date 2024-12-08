from django.db import models

from django.contrib.auth.models import User


class Dish(models.Model):
    author = models.ForeignKey(User)
    description = models.TextField()
    is_vegetarian = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Dishes"


class Image(models.Model):
    dish = models.ForeignKey(Dish, related_name="images")
    image = models.ImageField(upload_to="dish_images")

    created_at = models.DateTimeField(auto_now_add=True)


class Guess(models.Model):
    user = models.ForeignKey(User)
    dish = models.ForeignKey(Dish)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Guesses"


class NutritionalData(models.Model):
    calories = models.IntegerField(blank=True, null=True)
    fat = models.IntegerField(blank=True, null=True)
    carbohydrates = models.IntegerField(blank=True, null=True)
    protein = models.IntegerField(blank=True, null=True)

    cholesterol = models.IntegerField(blank=True, null=True)
    fibre = models.IntegerField(blank=True, null=True)
    sugar = models.IntegerField(blank=True, null=True)
    sodium = models.IntegerField(blank=True, null=True)

    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NutritionalDataDish(NutritionalData):
    dish = models.OneToOneField(Dish, related_name="nutritional_data")


class NutritionalDataGuess(NutritionalData):
    guess = models.OneToOneField(Guess, related_name="nutritional_data")
