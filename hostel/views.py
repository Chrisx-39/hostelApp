from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q, Count, F, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import date, timedelta
from django.utils import timezone
from .models import User, Room, Occupancy, Payment, Issue


# ==================== DECORATORS ====================
def user_role_required(roles):
    """Decorator to check user role permissions"""
    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


# ==================== AUTHENTICATION VIEWS ====================
@require_http_methods(["GET", "POST"])
def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect based on role
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'hostel/login.html')


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


# ==================== DASHBOARD VIEW ====================
@login_required
def dashboard(request):
    """Main dashboard view with role-based data"""
    context = {}
    
    # Common stats for all roles
    common_stats = {
        'total_rooms': Room.objects.count(),
        'occupied_rooms': Room.objects.filter(status='occupied').count(),
        'vacant_rooms': Room.objects.filter(status='available', current_occupancy__lt=F('capacity')).count(),
        'maintenance_rooms': Room.objects.filter(status='maintenance').count(),
        'total_students': User.objects.filter(role='student').count(),
        'active_occupancies': Occupancy.objects.filter(is_active=True).count(),
    }
    context.update(common_stats)
    
    if request.user.role in ['admin', 'manager']:
        # Admin/Manager specific data
        admin_stats = {
            'pending_payments': Payment.objects.filter(status='pending').count(),
            'overdue_payments': Payment.objects.filter(
                status='pending', 
                due_date__lt=date.today()
            ).count(),
            'open_issues': Issue.objects.filter(status__in=['open', 'in_progress']).count(),
            'urgent_issues': Issue.objects.filter(priority='urgent', status__in=['open', 'in_progress']).count(),
            'recent_issues': Issue.objects.select_related('room', 'reported_by')
                                .order_by('-reported_date')[:5],
            'recent_payments': Payment.objects.select_related('occupancy__student', 'occupancy__room')
                                  .order_by('-created_at')[:5],
            'recent_occupancies': Occupancy.objects.select_related('student', 'room')
                                    .filter(is_active=True)
                                    .order_by('-check_in_date')[:5],
        }
        context.update(admin_stats)
    else:
        # Student specific data
        try:
            occupancy = Occupancy.objects.select_related('room').get(
                student=request.user, 
                is_active=True
            )
            student_data = {
                'current_occupancy': occupancy,
                'my_payments': Payment.objects.filter(occupancy=occupancy)
                                  .select_related('occupancy__room')
                                  .order_by('-due_date')[:5],
                'my_issues': Issue.objects.filter(reported_by=request.user)
                                .select_related('room')
                                .order_by('-reported_date')[:5],
                'total_paid': Payment.objects.filter(
                    occupancy=occupancy, 
                    status='completed'
                ).aggregate(total=Sum('amount'))['total'] or 0,
                'pending_payments': Payment.objects.filter(
                    occupancy=occupancy, 
                    status='pending'
                ).count(),
            }
            context.update(student_data)
        except Occupancy.DoesNotExist:
            context['current_occupancy'] = None
            messages.info(request, 'You are not currently assigned to any room.')
    
    return render(request, 'hostel/dashboard.html', context)


# ==================== ROOM VIEWS ====================
@login_required
def room_list(request):
    """List all rooms with filtering and tabbed interface"""
    rooms = Room.objects.all().prefetch_related('occupancies__student').order_by('room_number')
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    
    # Calculate statistics
    stats = {
        'total_count': rooms.count(),
        'vacant_count': rooms.filter(status='available', current_occupancy__lt=F('capacity')).count(),
        'occupied_count': rooms.filter(status='occupied').count(),
        'maintenance_count': rooms.filter(status='maintenance').count(),
    }
    
    # Get filtered room sets for tabs
    room_sets = {
        'all_rooms': rooms,
        'vacant_rooms': rooms.filter(status='available', current_occupancy__lt=F('capacity')),
        'occupied_rooms': rooms.filter(status='occupied'),
        'maintenance_rooms': rooms.filter(status='maintenance'),
    }
    
    context = {
        **stats,
        **room_sets,
        'current_status_filter': status_filter,
    }
    
    return render(request, 'hostel/room_list.html', context)


@login_required
def room_detail(request, room_id):
    """Room detail view with occupants and issues"""
    room = get_object_or_404(
        Room.objects.prefetch_related('occupancies__student', 'issues__reported_by'), 
        id=room_id
    )
    
    active_occupancies = room.occupancies.filter(is_active=True)
    recent_issues = room.issues.all().order_by('-reported_date')[:10]
    
    context = {
        'room': room,
        'occupancies': active_occupancies,
        'issues': recent_issues,
    }
    return render(request, 'hostel/room_detail.html', context)


@login_required
@user_role_required(['admin', 'manager'])
@require_http_methods(["GET", "POST"])
def room_create(request):
    """Create a new room"""
    if request.method == 'POST':
        try:
            room = Room.objects.create(
                room_number=request.POST.get('room_number').strip(),
                capacity=int(request.POST.get('capacity', 1)),
                room_type=request.POST.get('room_type', 'Standard'),
                monthly_rent=request.POST.get('monthly_rent'),
                description=request.POST.get('description', '').strip(),
                amenities=request.POST.get('amenities', '').strip(),
            )
            messages.success(request, f'Room {room.room_number} created successfully!')
            return redirect('room_detail', room_id=room.id)
            
        except Exception as e:
            messages.error(request, f'Error creating room: {str(e)}')
    
    return render(request, 'hostel/room_form.html', {'action': 'Create'})


@login_required
@user_role_required(['admin', 'manager'])
@require_http_methods(["GET", "POST"])
def room_edit(request, room_id):
    """Edit an existing room"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        try:
            room.room_number = request.POST.get('room_number', room.room_number)
            room.capacity = int(request.POST.get('capacity', room.capacity))
            room.room_type = request.POST.get('room_type', room.room_type)
            room.monthly_rent = request.POST.get('monthly_rent', room.monthly_rent)
            room.description = request.POST.get('description', room.description)
            room.amenities = request.POST.get('amenities', room.amenities)
            room.status = request.POST.get('status', room.status)
            room.save()
            
            messages.success(request, f'Room {room.room_number} updated successfully!')
            return redirect('room_detail', room_id=room.id)
            
        except Exception as e:
            messages.error(request, f'Error updating room: {str(e)}')
    
    return render(request, 'hostel/room_form.html', {'action': 'Edit', 'room': room})


@login_required
@user_role_required(['admin', 'manager'])
def room_delete(request, room_id):
    """Delete a room"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        room_number = room.room_number
        room.delete()
        messages.success(request, f'Room {room_number} deleted successfully!')
        return redirect('room_list')
    
    return render(request, 'hostel/confirm_delete.html', {'object': room, 'type': 'room'})


# ==================== OCCUPANCY VIEWS ====================
@login_required
@user_role_required(['admin', 'manager'])
def occupancy_list(request):
    """List all occupancies with filtering"""
    occupancies = Occupancy.objects.select_related('student', 'room').all()
    
    active_filter = request.GET.get('active')
    if active_filter == 'true':
        occupancies = occupancies.filter(is_active=True)
    elif active_filter == 'false':
        occupancies = occupancies.filter(is_active=False)
    
    context = {
        'occupancies': occupancies.order_by('-check_in_date'),
        'active_filter': active_filter,
    }
    return render(request, 'hostel/occupancy_list.html', context)


@login_required
@user_role_required(['admin', 'manager'])
@require_http_methods(["GET", "POST"])
def occupancy_create(request):
    """Create a new occupancy"""
    if request.method == 'POST':
        try:
            room = get_object_or_404(Room, id=request.POST.get('room'))
            student = get_object_or_404(User, id=request.POST.get('student'))
            
            if not room.is_available:
                messages.error(request, 'Selected room is not available for occupancy!')
                return redirect('occupancy_create')
            
            # Check if student already has active occupancy
            if Occupancy.objects.filter(student=student, is_active=True).exists():
                messages.error(request, 'Student already has an active occupancy!')
                return redirect('occupancy_create')
            
            occupancy = Occupancy.objects.create(
                student=student,
                room=room,
                check_in_date=request.POST.get('check_in_date'),
                bed_number=request.POST.get('bed_number'),
                emergency_contact_name=request.POST.get('emergency_contact_name'),
                emergency_contact_phone=request.POST.get('emergency_contact_phone'),
                notes=request.POST.get('notes', ''),
            )
            
            messages.success(request, f'Occupancy created for {student.get_full_name() or student.username}!')
            return redirect('occupancy_list')
            
        except Exception as e:
            messages.error(request, f'Error creating occupancy: {str(e)}')
    
    context = {
        'rooms': Room.objects.filter(status='available', current_occupancy__lt=F('capacity')),
        'students': User.objects.filter(role='student'),
    }
    return render(request, 'hostel/occupancy_form.html', context)


@login_required
@user_role_required(['admin', 'manager'])
def occupancy_checkout(request, occupancy_id):
    """Checkout student from occupancy"""
    occupancy = get_object_or_404(Occupancy, id=occupancy_id)
    
    if request.method == 'POST':
        try:
            occupancy.check_out_date = date.today()
            occupancy.is_active = False
            occupancy.save()
            
            messages.success(request, f'{occupancy.student.username} checked out successfully!')
            return redirect('occupancy_list')
            
        except Exception as e:
            messages.error(request, f'Error during checkout: {str(e)}')
    
    return render(request, 'hostel/confirm_checkout.html', {'occupancy': occupancy})


# ==================== PAYMENT VIEWS ====================
@login_required
def payment_list(request):
    """List payments with role-based filtering"""
    if request.user.role in ['admin', 'manager']:
        payments = Payment.objects.select_related('occupancy__student', 'occupancy__room').all()
    else:
        # Student can only see their own payments
        occupancy = Occupancy.objects.filter(student=request.user, is_active=True).first()
        payments = Payment.objects.filter(occupancy=occupancy) if occupancy else Payment.objects.none()
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    context = {
        'payments': payments.order_by('-due_date'),
        'status_filter': status_filter,
    }
    return render(request, 'hostel/payment_list.html', context)


@login_required
@user_role_required(['admin', 'manager'])
@require_http_methods(["GET", "POST"])
def payment_create(request):
    """Create a new payment record"""
    if request.method == 'POST':
        try:
            occupancy = get_object_or_404(Occupancy, id=request.POST.get('occupancy'))
            
            payment = Payment.objects.create(
                occupancy=occupancy,
                amount=request.POST.get('amount'),
                payment_type=request.POST.get('payment_type'),
                payment_method=request.POST.get('payment_method', 'Cash'),
                due_date=request.POST.get('due_date'),
                notes=request.POST.get('notes', '').strip(),
            )
            
            messages.success(request, 'Payment record created successfully!')
            return redirect('payment_list')
            
        except Exception as e:
            messages.error(request, f'Error creating payment: {str(e)}')
    
    context = {
        'occupancies': Occupancy.objects.filter(is_active=True)
                          .select_related('student', 'room')
                          .order_by('student__username'),
    }
    return render(request, 'hostel/payment_form.html', context)


@login_required
@user_role_required(['admin', 'manager'])
@require_http_methods(["POST"])
def payment_update_status(request, payment_id):
    """Update payment status (AJAX compatible)"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    try:
        new_status = request.POST.get('status')
        payment.status = new_status
        
        if new_status == 'completed':
            payment.payment_date = date.today()
            payment.transaction_id = request.POST.get('transaction_id', '').strip()
        
        payment.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'status': payment.status})
        else:
            messages.success(request, 'Payment status updated successfully!')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        else:
            messages.error(request, f'Error updating payment: {str(e)}')
    
    return redirect('payment_list')


# ==================== ISSUE VIEWS ====================
@login_required
def issue_list(request):
    """List issues with role-based access"""
    if request.user.role in ['admin', 'manager']:
        issues = Issue.objects.select_related('room', 'reported_by', 'assigned_to').all()
    else:
        issues = Issue.objects.filter(reported_by=request.user).select_related('room')
    
    # Apply filters
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    if status_filter:
        issues = issues.filter(status=status_filter)
    if priority_filter:
        issues = issues.filter(priority=priority_filter)
    
    context = {
        'issues': issues.order_by('-reported_date'),
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'hostel/issue_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def issue_create(request):
    """Create a new issue report"""
    if request.method == 'POST':
        try:
            if request.user.role == 'student':
                # Students can only report issues for their own room
                occupancy = Occupancy.objects.filter(student=request.user, is_active=True).first()
                if not occupancy:
                    messages.error(request, 'You must be assigned to a room to report issues.')
                    return redirect('dashboard')
                room = occupancy.room
            else:
                # Staff can report issues for any room
                room = get_object_or_404(Room, id=request.POST.get('room'))
            
            issue = Issue.objects.create(
                reported_by=request.user,
                room=room,
                title=request.POST.get('title').strip(),
                description=request.POST.get('description').strip(),
                category=request.POST.get('category'),
                priority=request.POST.get('priority', 'medium'),
            )
            
            messages.success(request, 'Issue reported successfully!')
            return redirect('issue_list')
            
        except Exception as e:
            messages.error(request, f'Error reporting issue: {str(e)}')
    
    context = {}
    if request.user.role in ['admin', 'manager']:
        context['rooms'] = Room.objects.all().order_by('room_number')
    
    return render(request, 'hostel/issue_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def issue_detail(request, issue_id):
    """Issue detail view with update functionality"""
    issue = get_object_or_404(
        Issue.objects.select_related('room', 'reported_by', 'assigned_to'), 
        id=issue_id
    )
    
    # Permission check
    if request.user.role == 'student' and issue.reported_by != request.user:
        messages.error(request, 'You can only view your own issues.')
        return redirect('issue_list')
    
    if request.method == 'POST' and request.user.role in ['admin', 'manager']:
        try:
            issue.status = request.POST.get('status', issue.status)
            issue.assigned_to_id = request.POST.get('assigned_to') or None
            issue.resolution_notes = request.POST.get('resolution_notes', '').strip()
            
            if issue.status in ['resolved', 'closed'] and not issue.resolved_date:
                issue.resolved_date = timezone.now()
            
            issue.save()
            messages.success(request, 'Issue updated successfully!')
            return redirect('issue_detail', issue_id=issue.id)
            
        except Exception as e:
            messages.error(request, f'Error updating issue: {str(e)}')
    
    context = {
        'issue': issue,
        'staff_users': User.objects.filter(role__in=['admin', 'manager']) if request.user.role in ['admin', 'manager'] else None,
    }
    return render(request, 'hostel/issue_detail.html', context)


# ==================== AJAX VIEWS ====================
@login_required
def room_details_ajax(request, room_id):
    """AJAX endpoint for room details"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    room = get_object_or_404(Room, id=room_id)
    
    # Get active occupancies with student details
    active_occupancies = room.occupancies.filter(is_active=True).select_related('student')
    occupants_data = []
    
    for occupancy in active_occupancies:
        occupants_data.append({
            'name': occupancy.student.get_full_name() or occupancy.student.username,
            'check_in_date': occupancy.check_in_date.strftime('%Y-%m-%d'),
            'bed_number': occupancy.bed_number,
            'emergency_contact': f"{occupancy.emergency_contact_name} - {occupancy.emergency_contact_phone}",
        })
    
    room_data = {
        'id': room.id,
        'number': room.room_number,
        'type': room.room_type,
        'status': room.status,
        'price': float(room.monthly_rent),
        'capacity': room.capacity,
        'current_occupancy': room.current_occupancy,
        'occupants': occupants_data,
        'description': room.description or 'No description available',
        'amenities': [amenity.strip() for amenity in room.amenities.split(',')] if room.amenities else [],
        'is_available': room.is_available,
        'occupancy_percentage': room.occupancy_percentage,
    }
    
    return JsonResponse(room_data)


@login_required
@user_role_required(['admin', 'manager'])
def dashboard_stats_ajax(request):
    """AJAX endpoint for dashboard statistics"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    stats = {
        'total_rooms': Room.objects.count(),
        'occupied_rooms': Room.objects.filter(status='occupied').count(),
        'vacant_rooms': Room.objects.filter(status='available', current_occupancy__lt=F('capacity')).count(),
        'maintenance_rooms': Room.objects.filter(status='maintenance').count(),
        'pending_payments': Payment.objects.filter(status='pending').count(),
        'overdue_payments': Payment.objects.filter(status='pending', due_date__lt=date.today()).count(),
        'open_issues': Issue.objects.filter(status__in=['open', 'in_progress']).count(),
    }
    
    return JsonResponse(stats)