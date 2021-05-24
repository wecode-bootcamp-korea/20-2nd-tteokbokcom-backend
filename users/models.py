from django.db import models

class User(models.Model):

    username          = models.CharField(max_length=45, blank=False)
    introduction      = models.TextField(null=True)
    email             = models.EmailField(max_length=254, unique=True, blank=False)
    password          = models.CharField(max_length=65, blank=False)
    profile_image_url = models.URLField(max_length=2000)

    class Meta:
        db_table = "users"

    def __str__(self):
        return f'{self.id}: {self.email} | {self.username}'

class Likes(models.Model):

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)

    class Meta():
        db_table = 'likes'

    def __str__(self):
        return f'{self.user.username} : {self.project.title}'