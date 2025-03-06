from django.contrib import admin
from django.utils.html import format_html
from users.models import CustomUser

class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone_number", "email", "is_active", "is_admin", "is_deleted", "profile_picture_preview")
    list_editable = ("phone_number", "is_active", "is_admin", "is_deleted")
    list_filter = ("is_active", "is_admin", "is_deleted", "date_joined")
    search_fields = ("first_name", "last_name", "phone_number", "email")
    readonly_fields = ("date_joined", "last_login", "profile_picture_preview")
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_admin', 'is_deleted', 'is_staff', 'is_superuser')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )
    actions = ["make_inactive", "make_admin", "delete_users"]
    ordering = ("first_name", "last_name")
    list_per_page = 50

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_preview.short_description = "Profile Picture"

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = "Active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected users as inactive"

    def make_admin(self, request, queryset):
        queryset.update(is_admin=True)
    make_admin.short_description = "Mark selected users as admin"

    def delete_users(self, request, queryset):
        queryset.update(is_deleted=True)
    delete_users.short_description = "Soft delete selected users"
    
class SampleUserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone_number", "email", "is_active", "is_admin", "is_deleted")
    list_editable = ("phone_number", "is_active", "is_admin", "is_deleted")
    list_filter = ("is_active", "is_admin", "is_deleted", "date_joined")
    search_fields = ("first_name", "last_name", "phone_number", "email")
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_admin', 'is_deleted', 'is_staff', 'is_superuser')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )
    ordering = ("first_name", "last_name")
    list_per_page = 50
    
admin.site.register(CustomUser, SampleUserAdmin)