from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from rest_framework import viewsets
from django.contrib.auth import update_session_auth_hash
from .models import User
from .serializers import (
    RequestPasswordResetSerializer,
    SetNewPasswordSerializer,
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    ChangePasswordSerializer
)
# from .permissions import IsOwnerOrReadOnly

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Issue tokens right after registration
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class SigninView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
            
        return Response({
            'user': UserSerializer(user).data,
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
# class SignOutView(APIView):
#     serializer_class = UserLoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data, context={'request':request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         refresh = RefreshToken.for_user(user)
            
#         return Response({
#             'user': UserSerializer(user).data,
#             'refresh_token': str(refresh),
#             'access_token': str(refresh.access_token),
#         }, status=status.HTTP_200_OK)

class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Support both 'refresh' and 'refresh_token' keys from the frontend
            refresh_token = request.data.get("refresh") or request.data.get("refresh_token")
            
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": "Successfully logged out."}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        
        # # Check old password
        # if not user.check_password(serializer.validated_data['old_password']):
        #     return Response(
        #         {"old_password": ["Wrong password."]}, 
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Update session auth hash to keep user logged in
        update_session_auth_hash(request, user)
        
        return Response(
            {"message": "Password updated successfully"}, 
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# users/views.py


@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    serializer = RequestPasswordResetSerializer(
        data=request.data,
        context={"request": request}
    )
    serializer.is_valid(raise_exception=True)

    return Response({"message": "If this email exists, a reset link has been sent"})


@api_view(["POST"])
@permission_classes([AllowAny])
def set_new_password(request):
    serializer = SetNewPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response({"message": "Password reset successful"})

