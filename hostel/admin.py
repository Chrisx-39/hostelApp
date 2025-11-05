from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Room, Occupancy, Payment, Issue

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'phone', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address', 'profile_picture')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address')}),
    )

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'capacity', 'current_occupancy', 'status', 'monthly_rent']
    list_filter = ['status', 'capacity']
    search_fields = ['room_number', 'description']

@admin.register(Occupancy)
class OccupancyAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'bed_number', 'check_in_date', 'check_out_date', 'is_active']
    list_filter = ['is_active', 'check_in_date']
    search_fields = ['student__username', 'room__room_number']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['occupancy', 'amount', 'payment_type', 'status', 'due_date', 'payment_date']
    list_filter = ['status', 'payment_type', 'due_date']
    search_fields = ['occupancy__student__username', 'transaction_id']

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'room', 'reported_by', 'category', 'priority', 'status', 'reported_date']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['title', 'description', 'room__room_number']
