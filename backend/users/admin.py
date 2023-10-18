from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Для модели User создана кастомная админка."""
    list_display = ('username', 'id',
                    'email', 'first_name',
                    'last_name')
    list_filter = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Для модели Subscription создана кастомная админка."""
    list_display = ('user', 'author')
