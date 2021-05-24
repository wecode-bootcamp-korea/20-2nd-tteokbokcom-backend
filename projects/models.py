from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "categories"

class Tag(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "tags"