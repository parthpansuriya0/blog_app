from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    username = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
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
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'id': self.id})

class Comment(models.Model):
    blog_title = models.ForeignKey(Blog,on_delete=models.CASCADE,related_name="commnettitle")
    comment_detail = models.TextField()
    comment_by = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="commentby")
    comment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        if len(self.comment_detail) > 75:
            title = self.comment_detail[:75] + "..."
        else:
            title = self.comment_detail
        return title
    
    def get_absolute_url(self):
        return reverse('comment_page', kwargs={'id': self.id})