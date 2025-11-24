from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_partner_notification(vehicle, action_type, details):
    partners = vehicle.partners.filter(is_active=True)

    if not partners.exists():
        return

    recipient_emails = [partner.email for partner in partners if partner.email]

    if not recipient_emails:
        return

    if action_type == 'rental':
        subject = f'New Rental Added - {vehicle.name}'
        message = f"""
New Rental Added to {vehicle.name} ({vehicle.registration_number})

Customer: {details.get('customer_name', 'N/A')}
Date Out: {details.get('date_out', 'N/A')}
Destination: {details.get('destination', 'N/A')}
Days: {details.get('days_of_rent', 'N/A')}
Amount Received: ₹{details.get('total_amount_received', '0')}

This is an automated notification from Vehicle Manager.
        """

    elif action_type == 'expense':
        subject = f'New Expense Added - {vehicle.name}'
        message = f"""
New Expense Added to {vehicle.name} ({vehicle.registration_number})

Date: {details.get('date', 'N/A')}
Particulars: {details.get('particulars', 'N/A')}
Place: {details.get('place', 'N/A')}
Amount: ₹{details.get('amount', '0')}

This is an automated notification from Vehicle Manager.
        """

    elif action_type == 'emi_payment':
        subject = f'EMI Payment Made - {vehicle.name}'
        message = f"""
EMI Payment Made for {vehicle.name} ({vehicle.registration_number})

EMI Amount: ₹{details.get('amount', '0')}
Payment Date: {details.get('date', 'N/A')}
Month: {details.get('month', 'N/A')}

This is an automated notification from Vehicle Manager.
        """

    else:
        return

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_emails,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email notification failed: {str(e)}")
