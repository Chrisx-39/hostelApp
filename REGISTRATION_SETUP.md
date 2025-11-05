# Student Self-Registration with Email Verification

## Overview
This system allows students to register themselves for hostel management access with email verification. The system uses Django's built-in email functionality to send verification links.

## Features
✅ Student self-registration form
✅ Email validation and uniqueness checks
✅ Password strength requirements (min 6 characters)
✅ Email verification with 24-hour expiry tokens
✅ Resend verification email option
✅ Mobile-responsive design
✅ Secure token-based verification

## Setup Instructions

### 1. Create Database Migrations
Run these commands to create the necessary database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will:
- Add `email_verified` field to User model
- Create `EmailVerification` model table

### 2. Email Configuration

#### For Development (Console Backend - Default)
Emails will print to your console/terminal. No additional setup needed.
Already configured in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@hostelms.com'
```

#### For Production (Real Email)
Uncomment and configure in `settings.py`:

**Option 1: Gmail**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

**Gmail App Password Setup:**
1. Go to Google Account > Security
2. Enable 2-Step Verification
3. Generate App Password for "Mail"
4. Use the generated 16-character password

**Option 2: Other SMTP Providers**
- **Outlook**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **SendGrid/Mailgun**: Professional email services

### 3. Test the System

#### Start Development Server
```bash
python manage.py runserver
```

#### Test Registration Flow
1. Visit: `http://localhost:8000/register/`
2. Fill in registration form
3. Check console for verification email
4. Copy the verification link
5. Visit the link to activate account
6. Login at `http://localhost:8000/login/`

## URLs
- **Register**: `/register/`
- **Login**: `/login/`
- **Registration Success**: `/registration-success/`
- **Verify Email**: `/verify-email/<token>/`
- **Resend Verification**: `/resend-verification/`

## Registration Form Fields
- **First Name*** (required)
- **Last Name*** (required)
- **Username*** (required, min 3 characters, unique)
- **Email*** (required, valid email format, unique)
- **Phone** (optional)
- **Password*** (required, min 6 characters)
- **Confirm Password*** (required, must match)

## Validation Rules
- Username: minimum 3 characters, must be unique
- Email: valid format, must be unique
- Password: minimum 6 characters
- All passwords must match confirmation
- First and last names are required

## Security Features
- Passwords are hashed using Django's default algorithm
- Email tokens are UUID-based (impossible to guess)
- Tokens expire after 24 hours
- Accounts inactive until email verified
- Old tokens invalidated when resending verification

## User Flow

### 1. Registration
```
Student fills form → 
Data validated → 
User created (inactive) → 
Verification token created → 
Email sent → 
Redirect to success page
```

### 2. Email Verification
```
Student clicks email link → 
Token validated → 
User activated → 
Redirect to login
```

### 3. Login
```
Student logs in → 
Credentials verified → 
Redirect to dashboard
```

## Admin Panel
Administrators can view and manage:
- User accounts (`/admin/hostel/user/`)
- Email verifications (`/admin/hostel/emailverification/`)
- Manually activate accounts if needed

## Troubleshooting

### Emails Not Sending (Console Backend)
- Check terminal output where `runserver` is running
- Email content will appear in console

### Emails Not Sending (SMTP)
- Verify SMTP credentials
- Check firewall/antivirus isn't blocking port 587
- For Gmail, ensure App Password is used, not regular password
- Check spam folder

### Verification Link Expired
- User can request new verification via "Resend Verification" page
- Old tokens automatically invalidated

### User Already Exists
- Check if email/username already registered
- Admin can delete duplicate accounts from admin panel

## Database Models

### EmailVerification
```python
- user: ForeignKey to User
- token: UUID (unique)
- created_at: DateTime
- expires_at: DateTime (24 hours from creation)
- verified: Boolean
```

### User (Extended)
```python
- email_verified: Boolean (default: False)
# ... other existing fields
```

## Security Best Practices

1. **Production Checklist**:
   - Use HTTPS for verification links
   - Use environment variables for email credentials
   - Enable rate limiting on registration endpoint
   - Add CAPTCHA for spam prevention
   - Use professional email service (SendGrid, etc.)

2. **Email Security**:
   - Never commit email passwords to git
   - Use app-specific passwords
   - Rotate credentials regularly

3. **Token Security**:
   - Tokens are one-time use
   - Automatic expiry after 24 hours
   - UUID format prevents brute-force

## Customization

### Change Token Expiry
In `models.py` > `EmailVerification` > `save()`:
```python
self.expires_at = timezone.now() + timedelta(hours=48)  # 48 hours instead of 24
```

### Customize Email Template
In `views.py` > `register_view()`:
```python
email_message = f"""
Your custom email template here
"""
```

### Add Additional Validation
In `views.py` > `register_view()`:
```python
# Add custom validation
if not phone or len(phone) < 10:
    errors.append('Phone number is required')
```

## Testing Checklist
- [ ] Registration with valid data succeeds
- [ ] Duplicate username rejected
- [ ] Duplicate email rejected
- [ ] Invalid email format rejected
- [ ] Password mismatch rejected
- [ ] Short password rejected
- [ ] Email sent successfully
- [ ] Verification link works
- [ ] Expired link shows error
- [ ] Resend verification works
- [ ] Login after verification succeeds
- [ ] Login before verification fails

## Support
For issues or questions, contact the development team or check Django documentation:
- Django Email: https://docs.djangoproject.com/en/4.2/topics/email/
- Django Authentication: https://docs.djangoproject.com/en/4.2/topics/auth/
