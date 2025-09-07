from rest_framework import serializers
from .models import Post
import bleach


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model=Post
        fields= '__all__'
        read_only_fields= ['created_at', 'author','slug']

    def validate_content(self, value):
        allowed_tags = ['p','b','i','ul','ol','li','strong','em','a','img']
        allowed_attrs = {
            'a': ['href','title'],
            'img': ['src','alt','title'],
            }
        cleaned = bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
    )
        return cleaned

class PostListSerializer(serializers.ModelSerializer):
    content_slice=serializers.SerializerMethodField()

    class Meta:
        model=Post
        fields= ['id', 'title','content_slice', 'created_at','slug']
        

    def get_content_slice(self,obj):
        return obj.content[:100]+ '...'