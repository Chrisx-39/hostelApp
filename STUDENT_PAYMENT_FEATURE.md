# Student Payment Feature

## Overview
Students can now make payments for their hostel fees directly from their account. The system supports multiple payment methods including Mobile Money (MTN, Airtel), Bank Transfer, and Cash payments.

## Features Implemented

### ✅ For Students
- **View Payments**: See all pending and completed payments
- **Payment Details**: View detailed information about each payment
- **Multiple Payment Methods**:
  - MTN Mobile Money
  - Airtel Money  
  - Bank Transfer
  - Cash Payment
- **Payment Initiation**: Start the payment process online
- **Transaction Tracking**: Get unique transaction IDs
- **Payment Confirmation**: Receive confirmation after payment
- **Receipt View**: View and print receipts for completed payments

### ✅ For Administrators
- **Payment Management**: Continue to manage payments as before
- **Payment Verification**: Verify student-initiated payments
- **Transaction Records**: View transaction IDs and notes

## User Flow

### Student Payment Process

```
1. Student logs in to dashboard
2. Navigates to Payments section
3. Sees list of pending and completed payments
4. Clicks "Pay Now" on a pending payment
5. Selects payment method (Mobile Money/Bank/Cash)
6. For Mobile Money: Enters phone number
7. Clicks "Proceed to Pay"
8. System generates transaction ID
9. Student receives confirmation page
10. For Mobile Money: Completes payment on phone
11. Admin verifies and marks payment as completed
12. Student can view receipt
```

## New URLs

- `/payments/<id>/detail/` - Payment details page
- `/payments/<id>/pay/` - Payment method selection
- `/payments/<id>/confirmation/` - Payment confirmation page

## Payment Methods

### 1. Mobile Money (MTN & Airtel)
**For Students:**
- Select MTN Mobile Money or Airtel Money
- Enter phone number
- Initiate payment
- Check phone for payment prompt
- Enter PIN to confirm

**For Production:**
- Integrate with MTN MoMo API
- Integrate with Airtel Money API
- Automatic payment verification

### 2. Bank Transfer
**For Students:**
- View bank account details
- Make transfer using transaction ID as reference
- Submit transfer confirmation

**Bank Details (Example):**
```
Account: 1234567890
Bank: Zanaco Bank
Branch: Main Branch
Reference: Transaction ID
```

### 3. Cash Payment
**For Students:**
- Select cash payment option
- Get transaction reference number
- Visit hostel office during business hours
- Make payment with reference number

**Office Hours:**
```
Monday - Friday: 8:00 AM - 5:00 PM
Saturday: 9:00 AM - 1:00 PM
```

## Technical Implementation

### Models
No new models were added. Using existing `Payment` model with enhanced fields:
- `payment_method`: Stores selected payment method
- `transaction_id`: Unique transaction identifier
- `notes`: Additional payment information

### Views Added

#### `student_payment_detail()`
- Displays payment details
- Shows "Pay Now" button for pending payments
- Displays receipt for completed payments
- Security: Students can only view their own payments

#### `student_make_payment()`
- Payment method selection form
- Mobile number input for mobile money
- Payment initiation logic
- Transaction ID generation
- Security: Students can only pay their own bills

#### `student_payment_confirmation()`
- Confirmation page after payment initiation
- Payment instructions based on method
- Transaction details display
- Next steps guidance

### Templates Created

1. **`student_payment_detail.html`**
   - Payment information card
   - Status badges
   - Action buttons
   - Receipt view for completed payments

2. **`student_make_payment.html`**
   - Payment method accordion
   - Mobile money options (MTN, Airtel)
   - Bank transfer details
   - Cash payment instructions
   - Phone number validation

3. **`student_payment_confirmation.html`**
   - Success message
   - Transaction details
   - Method-specific instructions
   - Important information

### Security Features
- Role-based access control
- Payment ownership verification
- CSRF protection
- Input validation
- Secure transaction IDs (UUID-based)

## Testing

### Manual Testing Checklist

**As Student:**
- [ ] Login as student
- [ ] View payments list
- [ ] Click "Pay Now" on pending payment
- [ ] Select MTN Mobile Money with phone number
- [ ] Complete payment process
- [ ] View confirmation page
- [ ] Check transaction ID is generated
- [ ] Go back to payments list
- [ ] Try selecting Airtel Money
- [ ] Try selecting Bank Transfer
- [ ] Try selecting Cash Payment
- [ ] View completed payment receipt
- [ ] Try to access another student's payment (should fail)

**As Admin:**
- [ ] View all payments
- [ ] See student-initiated payments with notes
- [ ] Verify transaction IDs
- [ ] Update payment status to completed
- [ ] Check payment shows as completed for student

## Production Integration

### Mobile Money APIs

#### MTN Mobile Money Integration
```python
# In views.py - student_make_payment()
# Replace demo code with actual MTN API call

import requests

def initiate_mtn_payment(phone_number, amount, reference):
    url = "https://momoapi.mtn.com/collection/v1_0/requesttopay"
    headers = {
        "Authorization": f"Bearer {MTN_API_KEY}",
        "X-Target-Environment": "production",
        "Content-Type": "application/json"
    }
    data = {
        "amount": str(amount),
        "currency": "ZMW",
        "externalId": reference,
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": phone_number
        },
        "payerMessage": "Hostel Payment",
        "payeeNote": "Payment for hostel fees"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
```

#### Airtel Money Integration
```python
# Similar integration with Airtel Money API
def initiate_airtel_payment(phone_number, amount, reference):
    # Implement Airtel Money API call
    pass
```

### Environment Variables
Add to `.env` or `settings.py`:
```python
MTN_API_KEY = 'your-mtn-api-key'
MTN_API_SECRET = 'your-mtn-secret'
AIRTEL_API_KEY = 'your-airtel-api-key'
AIRTEL_API_SECRET = 'your-airtel-secret'
```

### Payment Webhook
Create webhook endpoint for automatic payment confirmation:
```python
@csrf_exempt
def payment_webhook(request):
    """Receive payment confirmation from payment gateway"""
    if request.method == 'POST':
        data = json.loads(request.body)
        transaction_id = data.get('reference')
        status = data.get('status')
        
        payment = Payment.objects.get(transaction_id=transaction_id)
        if status == 'SUCCESSFUL':
            payment.status = 'completed'
            payment.payment_date = date.today()
            payment.save()
            
            # Send confirmation email/SMS to student
            
        return JsonResponse({'status': 'received'})
```

## Configuration

### Update Settings
```python
# settings.py

# Payment Gateway Settings
PAYMENT_METHODS = {
    'MTN_MOBILE_MONEY': {
        'enabled': True,
        'api_key': os.getenv('MTN_API_KEY'),
    },
    'AIRTEL_MONEY': {
        'enabled': True,
        'api_key': os.getenv('AIRTEL_API_KEY'),
    },
    'BANK_TRANSFER': {
        'enabled': True,
        'account_number': '1234567890',
        'bank_name': 'Zanaco Bank',
        'branch': 'Main Branch',
    },
    'CASH': {
        'enabled': True,
        'office_hours': 'Mon-Fri: 8AM-5PM, Sat: 9AM-1PM',
    }
}
```

## Monitoring

### Payment Analytics
Track:
- Number of student-initiated payments
- Payment method preferences
- Payment success rates
- Average time to payment completion
- Failed payment reasons

### Admin Dashboard
Add widgets for:
- Pending student payments
- Recent payment confirmations
- Failed payment alerts
- Revenue tracking

## Future Enhancements

### Planned Features
1. **Automatic Payment Confirmation**: Real-time payment verification via API webhooks
2. **Payment Reminders**: Email/SMS reminders for overdue payments
3. **Payment Plans**: Installment payment options
4. **Mobile App Integration**: Native mobile app payments
5. **Payment History Export**: Download payment history as PDF/CSV
6. **Recurring Payments**: Auto-pay for monthly rent
7. **Payment Receipts**: Email receipts automatically
8. **Refund Management**: Handle refund requests
9. **Payment Analytics**: Student payment behavior insights
10. **Multi-currency Support**: Support for different currencies

### Technical Improvements
- Add payment retry logic
- Implement payment timeout handling
- Add payment validation middleware
- Create payment audit trail
- Add payment dispute resolution
- Implement payment notifications
- Add payment gateway failover

## Troubleshooting

### Common Issues

**Issue: Payment not showing as completed**
- Admin needs to manually verify and update status
- Check transaction ID matches
- Verify payment in gateway dashboard

**Issue: Mobile money payment not received**
- Check phone number format (+260...)
- Verify network connectivity
- Check mobile money account balance
- Contact support with transaction ID

**Issue: Can't access payment page**
- Ensure student has active occupancy
- Check user role is 'student'
- Verify payment belongs to student

**Issue: Transaction ID not generated**
- Check server logs for errors
- Verify UUID import in views
- Check database permissions

## Support

### For Students
- Transaction ID lookup
- Payment status inquiries
- Receipt reprints
- Payment method assistance

### For Administrators
- Payment verification tools
- Transaction reconciliation
- Refund processing
- Payment gateway support

## Security Considerations

1. **PCI DSS Compliance**: If storing card data
2. **Data Encryption**: Encrypt sensitive payment data
3. **Audit Logging**: Log all payment transactions
4. **Access Control**: Role-based payment access
5. **Fraud Detection**: Monitor suspicious payment patterns
6. **Rate Limiting**: Prevent payment spam
7. **Input Sanitization**: Validate all payment inputs
8. **Secure Communication**: Use HTTPS for all payment pages

## Conclusion

The student payment feature provides a seamless, secure way for students to manage their hostel payments online. With support for popular payment methods in Zambia (MTN, Airtel), students have flexible payment options while administrators maintain full control and visibility over all transactions.

For production deployment, integrate with actual payment gateway APIs and configure appropriate security measures.
