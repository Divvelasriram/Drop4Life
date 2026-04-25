import os


def send_emergency_alert(blood_group, hospital_name, location):
    """
    Sends emergency SMS alerts to matched blood group donors.
    Uses Twilio if configured, otherwise falls back to console logging.
    """
    from models import DonorProfile
    matched_donors = DonorProfile.query.filter_by(blood_group=blood_group).all()

    message_body = (
        f"URGENT: {hospital_name} at {location} needs {blood_group} blood immediately. "
        f"Please visit the hospital or check the Drop4Life App."
    )

    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_from = os.environ.get('TWILIO_PHONE_NUMBER')

    if twilio_sid and twilio_token and twilio_from:
        _send_sms_twilio(twilio_sid, twilio_token, twilio_from, matched_donors, message_body)
    else:
        _send_console_alert(blood_group, hospital_name, location, matched_donors, message_body)


def _send_sms_twilio(sid, token, from_number, donors, message_body):
    from twilio.rest import Client
    client = Client(sid, token)

    sent_count = 0
    for donor in donors:
        if not donor.phone:
            continue
        phone = donor.phone.strip()
        if not phone.startswith('+'):
            phone = '+91' + phone

        try:
            client.messages.create(body=message_body, from_=from_number, to=phone)
            sent_count += 1
            print(f"SMS sent to {donor.full_name} ({phone})")
        except Exception as e:
            print(f"Failed to send SMS to {donor.full_name}: {e}")

    print(f"Emergency SMS sent to {sent_count}/{len(donors)} matched donors.")


def _send_console_alert(blood_group, hospital_name, location, donors, message_body):
    print("=" * 50)
    print(f"EMERGENCY ALERT: {blood_group} BLOOD REQUIRED!")
    print(f"Hospital: {hospital_name}")
    print(f"Location: {location}")
    print(f"Matched donors ({blood_group}): {len(donors)}")
    for d in donors:
        print(f"  -> {d.full_name} | {d.phone}")
    print(f"Message: {message_body}")
    print("(Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER env vars to enable real SMS)")
    print("=" * 50)
