from django.urls import path
from .views import (
    dashboard,
    login_view,
    logout_view,
    register_view,
    registration_success,
    verify_email,
    resend_verification,
    room_list,
    room_detail,
    room_create,
    occupancy_list,
    occupancy_create,
    payment_list,
    payment_create,
    payment_update_status,
    student_payment_detail,
    student_make_payment,
    student_payment_confirmation,
    issue_list,
    issue_create,
    issue_detail,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('registration-success/', registration_success, name='registration_success'),
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification, name='resend_verification'),
    
    # Rooms
    path('rooms/', room_list, name='room_list'),
    path('rooms/<int:room_id>/', room_detail, name='room_detail'),
    path('rooms/create/', room_create, name='room_create'),
    path('rooms/<int:room_id>/edit/', room_create, name='room_edit'),
    
    # Occupancies
    path('occupancies/', occupancy_list, name='occupancy_list'),
    path('occupancies/create/', occupancy_create, name='occupancy_create'),
    
    # Payments
    path('payments/', payment_list, name='payment_list'),
    path('payments/create/', payment_create, name='payment_create'),
    path('payments/<int:payment_id>/update-status/', payment_update_status, name='payment_update_status'),
    path('payments/<int:payment_id>/detail/', student_payment_detail, name='student_payment_detail'),
    path('payments/<int:payment_id>/pay/', student_make_payment, name='student_make_payment'),
    path('payments/<int:payment_id>/confirmation/', student_payment_confirmation, name='student_payment_confirmation'),
    
    # Issues
    path('issues/', issue_list, name='issue_list'),
    path('issues/create/', issue_create, name='issue_create'),
    path('issues/<int:issue_id>/', issue_detail, name='issue_detail'),
]
