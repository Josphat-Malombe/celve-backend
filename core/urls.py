from django.urls import path


from .views import ( 
    RegisterView, 
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    ProfileView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CookieTokenObtainPairView.as_view(), name='cookie_login'),
    path('refresh/', CookieTokenRefreshView.as_view(), name='cookie_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile')
]

