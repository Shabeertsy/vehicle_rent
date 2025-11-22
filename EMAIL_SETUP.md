# Email Notification Setup Guide

## Gmail SMTP Configuration

This application sends email notifications to vehicle partners when:
- A new rental is added
- A new expense is added
- An EMI payment is made

### Step 1: Create a Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "How you sign in to Google", enable **2-Step Verification** (if not already enabled)
4. After enabling 2-Step Verification, go back to Security
5. Under "How you sign in to Google", click on **App passwords**
6. Select "Mail" as the app and "Other" as the device
7. Enter "Vehicle Manager" as the device name
8. Click "Generate"
9. **Copy the 16-character password** (you won't be able to see it again)

### Step 2: Update Django Settings

Open `/home/shabeer/Desktop/innova/vehicle_manager/settings.py` and update these lines:

```python
EMAIL_HOST_USER = 'your-actual-email@gmail.com'  # Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # Replace with the 16-character app password
DEFAULT_FROM_EMAIL = 'Vehicle Manager <your-actual-email@gmail.com>'
```

### Step 3: Test Email Configuration

You can test if emails are working by running this in Django shell:

```bash
python3 manage.py shell
```

Then in the shell:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email from Vehicle Manager.',
    settings.DEFAULT_FROM_EMAIL,
    ['recipient@example.com'],  # Replace with a test email
    fail_silently=False,
)
```

If successful, you should receive the test email!

### Email Notification Details

**When a rental is added:**
- Subject: "New Rental Added - [Vehicle Name]"
- Contains: Customer name, date, destination, days, amount

**When an expense is added:**
- Subject: "New Expense Added - [Vehicle Name]"
- Contains: Date, particulars, place, amount

**When EMI is paid:**
- Subject: "EMI Payment Made - [Vehicle Name]"
- Contains: EMI amount, payment date, month

### Important Notes

1. **Partner Email Required**: Partners must have a valid email address in their profile
2. **Active Partners Only**: Only active partners receive notifications
3. **Fail Silently**: Email failures won't stop the operation (rental/expense/EMI will still be saved)
4. **Gmail Limits**: Gmail has sending limits (500 emails/day for free accounts)

### Troubleshooting

**Emails not sending?**
- Check that 2-Step Verification is enabled
- Verify the app password is correct (no spaces)
- Check that EMAIL_HOST_USER matches the Gmail account
- Ensure partners have valid email addresses
- Check spam folder

**"Authentication failed" error?**
- Regenerate the app password
- Make sure you're using the app password, not your regular Gmail password
- Verify 2-Step Verification is enabled

### Alternative: Console Backend (Testing)

For testing without actual emails, you can use the console backend:

```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to the console instead of sending them.
