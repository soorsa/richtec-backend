from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    # AUTH VIEWS
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signin/', views.SigninView.as_view(), name='signin'),
    path('sign-out/', views.SignOutView.as_view(), name='sign-out'),
    path('logout/', views.logout_user, name = 'logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('change-password/', views.change_password, name='change-password'),
    path('forgot-password/', views.request_password_reset, name='forgot-password'),
    path('reset-password/', views.set_new_password, name='set-new-password'),

]
