from django.db import models

class Project(models.Model):
    title           = models.CharField(max_length=100)
    creater         = models.ForeignKey('users.User', on_delete=models.CASCADE)
    summary         = models.TextField()
    category        = models.ForeignKey("Category", on_delete=models.CASCADE)
    title_image_url = models.URLField(max_length=2000)
    target_fund     = models.DecimalField(max_digits=10, decimal_places=2)
    launch_date     = models.DateTimeField()
    end_date        = models.DateTimeField()
    created_at      = models.DateTimeField(auto_now_add=True)
    tag             = models.ManyToManyField("Tag", through="ProjectTag")

    class Meta:
        db_table = "projects"
    
    def __str__(self):
        return self.title

class ProjectTag(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    tag     = models.ForeignKey("Tag", on_delete=models.CASCADE)

    class Meta:
        db_table = "project_tags"

class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "categories"

class Tag(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "tags"

class FundingOption(models.Model):
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    project     = models.ForeignKey("Project", on_delete=models.CASCADE)
    remains     = models.IntegerField(null=True)
    title       = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        db_table = "funding_options"

class Donation(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    funding_option = models.ForeignKey("FundingOption", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "donations"