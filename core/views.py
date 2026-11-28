from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'register'


class MyLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    throttle_scope = 'login'


class MeView(APIView):
    def get(self, request):
        u = request.user
        return Response({
            'phone': u.phone,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'role': u.role,
        })