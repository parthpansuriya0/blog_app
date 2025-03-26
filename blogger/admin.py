from django.contrib import admin
from blogger.models import *

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1

class BlogAdmin(admin.ModelAdmin):
    inlines = [CommentInline]

admin.site.register(Blog,BlogAdmin)
admin.site.register(CustomUser)
admin.site.register(Comment)
