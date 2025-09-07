from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import Post
from .serializers import PostSerializer, PostListSerializer


# Create your views here.

class ListPosts(generics.ListAPIView):
    queryset=Post.objects.order_by('-created_at')[:3]
    serializer_class=PostSerializer
    
class ListPostsView(generics.ListAPIView):
    queryset=Post.objects.all()
    serializer_class=PostListSerializer

class CreatePost(generics.CreateAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    permission_classes=[IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug' 