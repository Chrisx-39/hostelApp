# Student Payment - Proof of Payment Upload Feature

## Overview
Students can now submit payments by uploading proof of payment (screenshots, receipts) instead of using payment gateways. This is simpler, more practical, and requires no third-party payment integrations.

## How It Works

### Student Process
1. Student makes payment via their preferred method (Mobile Money, Bank, Cash)
2. Student takes screenshot/photo of receipt or confirmation
3. Student logs in and goes to Payments section
4. Clicks "Pay Now" on pending payment
5. Selects payment method used
6. Uploads proof of payment (image or PDF)
7. Optionally enters transaction reference number
8. Submits for admin verification
9. Receives confirmation with transaction ID
10. Admin verifies and marks payment as completed

### Admin Process
1. Admin sees pending payments with "pending" status
2. Admin views uploaded proof of payment
3. Admin verifies the payment is legitimate
4. Admin updates status to "completed" with transaction ID
5. Student can now view receipt

## Setup Instructions

### 1. Run Migrations

**IMPORTANT**: You must run migrations to add the `proof_of_payment` field to the Payment model.

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

This adds the `proof_of_payment` ImageField to the Payment table.

### 2. Media Files Configuration

The uploaded proofs are stored in `media/payment_proofs/` directory.

**Verify settings.py** has media configuration (already configured):
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

**Add media URL pattern** to main `urls.py` if not already there:

```python
# In hostelmanager/urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your existing patterns
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3. Test the Feature

#### As Student:
```bash
1. Login as a student
2. Go to Payments
3. Click "Pay Now" on any pending payment
4. Select payment method (MTN, Airtel, Bank, or Cash)
5. Upload a screenshot or image (JPG, PNG) or PDF
6. Optionally add reference number
7. Click "Submit Payment"
8. See confirmation page
9. Check payment list - status should be "pending"
```

#### As Admin:
```bash
1. Login as admin/manager
2. Go to Payments
3. Find the student payment with status "pending"
4. Click the eye icon or view payment details
5. See the uploaded proof of payment image
6. Verify the payment
7. Update status to "completed"
8. Add transaction ID
9. Student can now see receipt
```

## File Upload Validations

### Allowed File Types
- **Images**: JPG, JPEG, PNG
- **Documents**: PDF
- **Max Size**: 5MB per file

### Validation in Code
The system validates:
- File extension (must be jpg, jpeg, png, or pdf)
- File size (max 5MB)
- Payment method selection (required)
- File upload (required)

### Error Messages
- "Please select a payment method"
- "Please upload proof of payment (screenshot or receipt)"
- "Please upload a valid image (JPG, PNG) or PDF file"
- "File size must be less than 5MB"

## URLs

| URL | Description | Access |
|-----|-------------|--------|
| `/payments/` | List all payments | Student/Admin |
| `/payments/<id>/detail/` | Payment details + proof | Student/Admin |
| `/payments/<id>/pay/` | Submit proof of payment | Student |
| `/payments/<id>/confirmation/` | Confirmation page | Student |

## Payment Status Flow

```
1. Created (by admin) → status: "pending"
2. Student uploads proof → status: "pending" (with proof_of_payment file)
3. Admin verifies → status: "completed" (with transaction_id)
```

## Database Changes

### Payment Model - New Field
```python
proof_of_payment = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
```

This field stores the uploaded proof file. Files are saved to `media/payment_proofs/`.

## Features

### ✅ For Students
- Simple upload interface
- Image preview before submission
- Multiple payment method options
- Reference number field (optional)
- Transaction ID for tracking
- Clear instructions
- Confirmation page
- View uploaded proof

### ✅ For Admins
- View uploaded proofs
- Verify payments manually
- Add transaction IDs
- Update payment status
- View all payment details
- Maintain full control

### ✅ Security
- Students can only upload to their own payments
- File type validation
- File size limits
- Secure file storage
- Role-based access control

## Mobile Responsive

All templates are **fully mobile-responsive**:
- File upload works on mobile cameras
- Touch-friendly buttons
- Responsive image preview
- Mobile-optimized forms

## Best Practices

### For Students
1. Take clear, legible screenshots
2. Ensure all details are visible
3. Include transaction ID/reference in image
4. Upload immediately after payment
5. Keep original receipts

### For Admins
1. Verify payment details match proof
2. Check transaction IDs
3. Confirm amounts
4. Update status promptly (within 24 hours)
5. Add notes if there are issues

## Common Student Payment Methods

### MTN Mobile Money
- Student pays via MTN MoMo
- Takes screenshot of confirmation SMS
- Uploads screenshot
- Transaction ID visible in screenshot

### Airtel Money
- Student pays via Airtel Money
- Takes screenshot of confirmation
- Uploads screenshot
- Reference number visible

### Bank Transfer
- Student transfers to hostel account
- Takes photo of bank receipt or screenshot of mobile banking
- Uploads proof
- Includes reference number

### Cash
- Student pays at hostel office
- Gets physical receipt
- Takes photo of receipt
- Uploads photo

## Troubleshooting

### Upload Not Working
- Check file size (must be < 5MB)
- Check file type (JPG, PNG, PDF only)
- Ensure internet connection stable
- Try different browser

### File Too Large
- Compress image before upload
- Take screenshot instead of photo
- Use lower resolution
- Convert to PDF if needed

### Can't See Uploaded Proof
- Ensure migrations ran successfully
- Check media folder permissions
- Verify MEDIA_URL in settings
- Check Django serving media files in development

### Admin Can't Verify
- Check user role (must be admin/manager)
- Ensure proof is visible in detail page
- Verify status update form works
- Check browser console for errors

## Future Enhancements

Possible additions:
- Email notification when payment verified
- SMS notification to student
- Automatic OCR to extract transaction details
- Payment proof quality check
- Bulk payment verification
- Payment analytics dashboard
- Export payment reports
- WhatsApp integration for proof upload

## Production Deployment

### Media Files in Production

1. **Use Cloud Storage** (Recommended):
```python
# Install django-storages
pip install django-storages boto3

# Configure S3 in settings.py
AWS_ACCESS_KEY_ID = 'your-key'
AWS_SECRET_ACCESS_KEY = 'your-secret'
AWS_STORAGE_BUCKET_NAME = 'hostel-payments'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

2. **Or Use Server Storage**:
- Ensure media directory has write permissions
- Set up proper backup system
- Configure nginx/apache to serve media files
- Set appropriate file size limits

### Security Considerations

1. **File Storage**:
   - Store media files outside web root
   - Use CDN for media serving
   - Regular backups of payment proofs

2. **Access Control**:
   - Verify user permissions before showing proofs
   - Implement rate limiting on uploads
   - Log all payment proof accesses

3. **File Validation**:
   - Scan uploaded files for malware
   - Validate image integrity
   - Prevent XSS through filenames

## Summary

This proof of payment system provides:
- ✅ Simple, no-gateway payment flow
- ✅ Manual admin verification
- ✅ Secure file uploads
- ✅ Mobile-friendly interface
- ✅ Complete audit trail
- ✅ Flexible payment methods
- ✅ Easy to test and deploy

**No payment gateway integrations needed!**
**No API keys required!**
**No monthly fees!**

Just upload, verify, done! 🎉
