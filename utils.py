import smtplib
from email.message import EmailMessage
import os

def send_emergency_alert(blood_group, hospital_name, location):
    """
    Simulated zero-cost notification system for Drop4Life.
    In a B.Tech Demo, printing to console confirms the logic works without
    requiring internet API integrations or exposing passwords.
    """
    print("="*50)
    print(f"🚨 EMERGENCY ALERT: {blood_group} BLOOD REQUIRED! 🚨")
    print(f"Hospital: {hospital_name}")
    print(f"Location: {location}")
    print("Sending notifications to matched donors in the area...")
    print("="*50)

    # --- Real Implementation Scaffold (Free via Gmail) ---
    # To activate real emails, students can uncomment below and provide credentials.
    
    # sender_email = os.environ.get('EMAIL_USER', 'your_email@gmail.com')
    # sender_password = os.environ.get('EMAIL_PASS', 'your_app_password')
    #
    # msg = EmailMessage()
    # msg.set_content(f"URGENT: {hospital_name} at {location} requires {blood_group} blood immediately. Please check the Drop4Life App.")
    # msg['Subject'] = f"Emergency {blood_group} Blood Request!"
    # msg['From'] = sender_email
    # msg['To'] = "registered_donor@example.com" # Would query DB for matches
    #
    # try:
    #     server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    #     server.login(sender_email, sender_password)
    #     server.send_message(msg)
    #     server.quit()
    #     print("Email dispatched successfully.")
    # except Exception as e:
    #     print(f"Failed to send email: {e}")
    #     pass

