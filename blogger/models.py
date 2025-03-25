from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    username = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'gender', 'age']

    def __str__(self):
        return self.username

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author_name = models.CharField(max_length=100)
    blogger_name = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="blogs")
    post_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

# class Comment(models.Model):
#     comment = models.TextField()
#     author_name = models.CharField(max_length=100)
#     blogger_name = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="blogs")
#     comment_date = models.DateField(auto_now_add=True)

#     def __str__(self):
#         return self.title

