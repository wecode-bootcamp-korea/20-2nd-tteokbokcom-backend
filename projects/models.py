from django.db import models

class Project(models.Model):
    title           = models.CharField(max_length=100)
    creater         = models.ForeignKey('users.User', on_delete=models.CASCADE)
    summary         = models.TextField()
    category        = models.ForeignKey("Category", on_delete=models.CASCADE)
    title_image_url = models.URLField(max_length=2000)
    target_fund     = models.DecimalField(max_digits=10, decimal_places=2)
    launch_data     = models.DateTimeField()
    end_data        = models.DateTimeField()
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projects"

class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "categories"

class Tag(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "tags"