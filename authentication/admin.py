# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User

# class CustomUserAdmin(UserAdmin):
#     list_display = ('email', 'first_name', 'last_name', 'role')
#     list_filter = ('is_staff', 'is_superuser', 'role', 'is_active')
#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('email',)
    
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'role', 'bio',)}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         # ('Referral', {'fields': ('referral_code', 'referral_earnings', 'referred_by')}),
#         # ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
#     )
    
#     # readonly_fields = ('created_at', 'updated_at')
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
#         ),
#     )

# admin.site.site_header = "Academy Admin Portal"
# admin.sites.AdminSite.site_title = "Academy Admin Portal"
# admin.site.index_title = "Welcome to Academy Admin Portal"
# admin.site.register(User, CustomUserAdmin)
# # admin.site.login_template = "users/login.html"

