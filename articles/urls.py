from django.urls import path
from .views import ListPosts, CreatePost,ListPostsView,ArticleDetailView


urlpatterns=[
    path('list/articles', ListPosts.as_view(), name='post-list'),
    path('main/articles', ListPostsView.as_view(), name="main-article"),
    path('main/articles/<slug:slug>/', ArticleDetailView.as_view(), name="detail-article"),
    path('create/articles', CreatePost.as_view(), name="create-article")

]