from rest_framework import serializers
from blogger.models import *

class BlogSerializer(serializers.HyperlinkedModelSerializer):
    id=serializers.ReadOnlyField()
    blogger_name = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'author_name','blogger_name','post_date']

class BloggerSerializer(serializers.HyperlinkedModelSerializer):
    id=serializers.ReadOnlyField()
    class Meta:
        model = CustomUser
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    id=serializers.ReadOnlyField()
    class Meta:
        model = Comment
        fields = ['id','blog_title', 'comment_detail','comment_by','comment_date']