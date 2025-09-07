from rest_framework import generics,permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken

from django.conf import settings




from .serializers import RegisterSerializer,ProfileSerializer
from django.contrib.auth import get_user_model



User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data['refresh']
            access_token = response.data['access']

            del response.data['refresh']

            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
                max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
            
            )
        return response
    
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT.get('AUTH_COOKIE', 'refresh_token'))
        if not refresh_token:
            return Response({'detail': 'Refresh token not found'}, status=400)

        data = request.data.copy()
        data['refresh'] = refresh_token

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except InvalidToken:
            return Response({'detail': 'Invalid refresh token'}, status=400)

        
        resp_data = serializer.validated_data.copy()
        response = Response(resp_data, status=200)

        if 'refresh' in serializer.validated_data:
            new_refresh = serializer.validated_data['refresh']
            if not settings.DEBUG:
                response.data.pop('refresh', None)

            response.set_cookie(
                key=settings.SIMPLE_JWT.get('AUTH_COOKIE', 'refresh_token'),
                value=new_refresh,
                httponly=True,
                secure=True,  
                samesite='None', 
                path='/',
                max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                
            )

        return response
    
class LogoutView(APIView):
    

    def post(self, request):
        response = Response({"detail": "Logout successful"}, status=200)

        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        return response
