from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Template)
admin.site.register(Image)
admin.site.register(Video)
admin.site.register(Card)
admin.site.register(Audio)
admin.site.register(Comment)