from django.urls import path
from .views import (
    dashboard,
    login_view,
    logout_view,
    room_list,
    room_detail,
    room_create,
    occupancy_list,
    occupancy_create,
    payment_list,
    payment_create,
    payment_update_status,
    issue_list,
    issue_create,
    issue_detail,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
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
    
    # Issues
    path('issues/', issue_list, name='issue_list'),
    path('issues/create/', issue_create, name='issue_create'),
    path('issues/<int:issue_id>/', issue_detail, name='issue_detail'),
]
