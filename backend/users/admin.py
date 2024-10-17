from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserActivity
import csv
from django.http import HttpResponse

# Define an Inline Model Admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False  # Prevent UserProfile deletion from user page
    verbose_name_plural = 'User Profile'  # Change the header name

# Extend the default UserAdmin class and add the UserProfileInline
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    # Fields you want to display in the user list view
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'get_institution', 'get_position')

    # Method to get the 'institution' field from user profile
    def get_institution(self, instance):
        return instance.userprofile.institution if hasattr(instance, 'userprofile') else None

    # Method to get the 'position' field from user profile
    def get_position(self, instance):
        return instance.userprofile.position if hasattr(instance, 'userprofile') else None

    # Name to be displayed in the column
    get_institution.short_description = 'Institution'

    # Name to be displayed in the column
    get_position.short_description = 'Position'

    # Function for exporting user data to CSV
    def export_users_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', 'First Name', 'Last Name', 'Is Superuser', 'Is Staff', 'Institution', 'Position'])
        for user in queryset:
            writer.writerow([
                user.username,
                user.first_name,
                user.last_name,
                user.is_superuser,
                user.is_staff,
                self.get_institution(user),
                self.get_position(user),
            ])
        return response

    # Short description for the action
    export_users_as_csv.short_description = "Export Selected Users as CSV"

    # Add the action to the admin interface
    actions = [export_users_as_csv]

# Unregister the default User model and register it with the custom admin class
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)





# Register a user Activity model
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'activity')
    search_fields = ('user',)
    list_filter = ('user',)

    # Function for exporting activity data to CSV
    def export_activity_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_activity.csv"'
        writer = csv.writer(response)
        writer.writerow(['User', 'Date', 'Activity'])
        for activity in queryset:
            writer.writerow([activity.user, activity.date, activity.activity])
        return response

    # Short description for the action
    export_activity_as_csv.short_description = "Export Selected Activity as CSV"

    # Add the action to the admin interface
    actions = [export_activity_as_csv]

admin.site.register(UserActivity, UserActivityAdmin)
