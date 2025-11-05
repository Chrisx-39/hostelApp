from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from datetime import timedelta
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Hostel Manager'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'

class Room(models.Model):
    ROOM_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    room_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    current_occupancy = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=15, choices=ROOM_STATUS, default='available')
    room_type = models.CharField(max_length=50, default='Standard')
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    description = models.TextField(blank=True)
    amenities = models.TextField(blank=True, help_text="Comma-separated amenities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rooms'
        ordering = ['room_number']
    
    def __str__(self):
        return f"Room {self.room_number}"
    
    @property
    def is_available(self):
        return self.current_occupancy < self.capacity and self.status == 'available'
    
    @property
    def occupancy_percentage(self):
        if self.capacity == 0:
            return 0
        return (self.current_occupancy / self.capacity) * 100

class Occupancy(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='occupancies')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='occupancies')
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    bed_number = models.CharField(max_length=5)
    is_active = models.BooleanField(default=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'occupancies'
        ordering = ['-check_in_date']
        unique_together = ['room', 'bed_number', 'is_active']
    
    def __str__(self):
        return f"{self.student.username} - Room {self.room.room_number}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_active = None
        
        if not is_new:
            old_occupancy = Occupancy.objects.get(pk=self.pk)
            old_active = old_occupancy.is_active
        
        super().save(*args, **kwargs)
        
        # Update room occupancy count
        if is_new and self.is_active:
            self.room.current_occupancy += 1
            self.room.save()
        elif not is_new and old_active != self.is_active:
            if self.is_active:
                self.room.current_occupancy += 1
            else:
                self.room.current_occupancy = max(0, self.room.current_occupancy - 1)
            self.room.save()

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_TYPE = [
        ('rent', 'Rent'),
        ('deposit', 'Security Deposit'),
        ('maintenance', 'Maintenance Fee'),
        ('other', 'Other'),
    ]
    
    occupancy = models.ForeignKey(Occupancy, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    payment_type = models.CharField(max_length=15, choices=PAYMENT_TYPE, default='rent')
    payment_method = models.CharField(max_length=50, default='Cash')
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    proof_of_payment = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.occupancy.student.username} - {self.payment_type} - ${self.amount}"
    
    @property
    def is_overdue(self):
        from datetime import date
        return self.status == 'pending' and self.due_date < date.today()

class Issue(models.Model):
    ISSUE_STATUS = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY = [
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('security', 'Security'),
        ('noise', 'Noise Complaint'),
        ('other', 'Other'),
    ]
    
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='issues')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=15, choices=CATEGORY, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY, default='medium')
    status = models.CharField(max_length=15, choices=ISSUE_STATUS, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    resolution_notes = models.TextField(blank=True)
    reported_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'issues'
        ordering = ['-reported_date']
    
    def __str__(self):
        return f"{self.title} - Room {self.room.room_number}"


class EmailVerification(models.Model):
    """Model to store email verification tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification for {self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.verified and not self.is_expired
