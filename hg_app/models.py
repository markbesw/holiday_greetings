from django.db import models
import re
from cloudinary.models import CloudinaryField
import random

# Create your models here.

class UserManager(models.Manager):
    def validate(self, postdata):
        email_check = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        if len(postdata['f_n']) < 2:
            errors['f_n'] = "First name must be 2 or more characters"
        if len(postdata['l_n']) < 2:
            errors['l_n'] = "Last name must be 2 or more characters"
        if not email_check.match(postdata['email']):
            errors['email'] = "Invalid email address"
        if len(postdata['pw']) < 8:
            errors['pw'] = "Password must be at least 8 characters"
        if postdata['pw'] != postdata['conf_pw']:
            errors['conf_pw'] = "Password does not match confirm password"
        return errors


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Template(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Image(models.Model):
    name = models.CharField(max_length=100)
    img = CloudinaryField('img', null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.pk}-{self.name}'
    
class Video(models.Model):
    name = models.CharField(max_length=100)
    vid = CloudinaryField('vid', null=True, resource_type='video')
    creator = models.ForeignKey(User,related_name='video_mgs', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.pk}-{self.name}'
    
class Audio(models.Model):
    name = models.CharField(max_length=100)
    aud = CloudinaryField('aud', null=True, resource_type='video')
    creator = models.ForeignKey(User,related_name='audio_mgs', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.pk}-{self.name}'
    
def rand_str():
    return str(random.randint(10000, 99999))
    
class Card(models.Model):
    name = models.CharField(max_length=50, blank=True)
    creator = models.ForeignKey(User,related_name='cards', on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    images = models.ManyToManyField(Image, related_name='cards', blank=True)
    video = models.ForeignKey(Video, related_name='cards', blank=True, null=True, on_delete=models.CASCADE)
    audio = models.ForeignKey(Audio, related_name='cards', blank=True, null=True, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, related_name='cards', blank=True, null=True, on_delete=models.CASCADE)
    granted = models.BooleanField(default=False)
    user_likes = models.ManyToManyField(User, related_name='liked_posts')
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    unique_id = models.CharField(max_length=10, default=rand_str())
    receiver_name = models.CharField(max_length=100, blank=True, null=True)
    receiver_email = models.CharField(max_length=100, blank=True, null=True)
    viewed = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.creator} card #{self.pk}'
    
class Comment(models.Model):
    content = models.TextField()
    poster = models.CharField(max_length=100)
    card = models.ForeignKey(Card, related_name="comments", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)