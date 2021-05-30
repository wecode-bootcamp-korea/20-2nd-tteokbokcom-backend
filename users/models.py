from django.db              import models
from django.forms.models    import model_to_dict

class User(models.Model):
    username               = models.CharField(max_length=40, blank=False)
    introduction           = models.TextField(null=True)
    email                  = models.EmailField(max_length=254, unique=True, blank=False)
    password               = models.CharField(max_length=65, blank=False)
    profile_image_url      = models.URLField(max_length=2000)
    kakao_id               = models.IntegerField(null=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return f'{self.id}: {self.email} | {self.username}'

    def to_dict(self, *args):
        return model_to_dict(self, exclude=[*args])
        
class Likes(models.Model):

    user    = models.ForeignKey('User', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)

    class Meta():
        db_table = 'likes'

    def __str__(self):
        return f'{self.user.username} : {self.project.title}'
