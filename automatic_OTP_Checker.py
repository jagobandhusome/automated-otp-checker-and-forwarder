import imaplib
import email
import re
import requests
from email.header import decode_header
import time
import datetime

EMAIL = "ivacbd@your_domain.com"
PASSWORD = "abc123"
IMAP_SERVER = "your_domain.com"
IMAP_PORT = 993
BATCH_ENDPOINT_1 = "https://abc.com/otp/update-external"  # First attempt URL
BATCH_ENDPOINT_2 = "https://abc.com/otp/otp-store-request"  # Fallback URL if the first fails

# Function to check the inbox and process new emails
def check_inbox():
    print("Connecting to the mail server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")  # Select the inbox
    print("Connection successful, searching for unread emails...")

    # Search for all unread emails
    result, data = mail.search(None, "UNSEEN")
    print("Search result:", result)
    print("Data:", data)

    if result == "OK":
        if data[0]:
            print("Found unread emails.")
            for num in data[0].split():
                print(f"Processing email {num}...")
                try:
                    result, msg_data = mail.fetch(num, "(RFC822)")
                    if result == "OK":
                        print(f"Fetched email {num} successfully.")
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])

                                # Decode the email subject
                                subject, encoding = decode_header(msg["Subject"])[0]
                                if isinstance(subject, bytes):
                                    subject = subject.decode(encoding if encoding else "utf-8")

                                print(f"Email subject: {subject}")

                                # Check if this is a Gmail forwarding confirmation email
                                sender = msg.get("From", "")
                                if "forwarding-noreply@google.com" in sender and "Gmail Forwarding Confirmation" in subject:
                                    print("This is a Gmail forwarding confirmation email. Skipping processing and keeping in inbox.")
                                    continue  # Skip processing this email

                                # Filter based on subject for OTP emails
                                if subject == "Your OTP for IVAC Panel":
                                    sender = msg.get("From")
                                    to = msg.get("To")

                                    print(f"Sender: {sender}")
                                    print(f"Recipient: {to}")

                                    # Check the sender
                                    if "onlinepayment@sslcommerz.com" in sender:
                                        # Check if this is a direct email or forwarded email
                                        phone_match = re.search(r"(\d{11})@mailvoo\.io", to)  # Match 11-digit phone number
                                        
                                        if phone_match:
                                            # Direct email - extract phone number from To field
                                            phone_number = phone_match.group(1)
                                            print(f"Valid phone number from direct email: {phone_number}")
                                        else:
                                            # Forwarded email - extract phone number from Return-Path
                                            return_path = msg.get("Return-Path", "")
                                            print(f"Return-Path: {return_path}")
                                            
                                            # Extract phone number from Return-Path using pattern matching
                                            phone_match = re.search(r"[=@](\d{11})[=@]mailvoo\.io", return_path)
                                            if phone_match:
                                                phone_number = phone_match.group(1)
                                                print(f"Valid phone number from forwarded email: {phone_number}")
                                            else:
                                                print(f"Invalid recipient in To or Return-Path. Deleting email.")
                                                mail.store(num, '+FLAGS', '\\Deleted')
                                                mail.expunge()
                                                continue

                                        # Get the email body
                                        body = ""
                                        if msg.is_multipart():
                                            for part in msg.walk():
                                                content_type = part.get_content_type()
                                                content_disposition = str(part.get("Content-Disposition"))

                                                if "attachment" not in content_disposition:
                                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                        else:
                                            body = msg.get_payload(decode=True).decode(errors='ignore')

                                        print(f"Email body: {body}")

                                        # Check for OTP format in the body
                                        otp_match = re.search(r"(\d{6})\s+is\s+your\s+One-Time\s+Password\s+for\s+IVAC\s+panel", body)

                                        if otp_match:
                                            otp = otp_match.group(1)
                                            print(f"Found OTP: {otp}")

                                            # Send OTP request to the first external URL
                                            url_1 = f"{BATCH_ENDPOINT_1}&phone={phone_number}&otp={otp}"
                                            print(f"Sending OTP request to: {url_1}")
                                            response = requests.get(url_1)

                                            if response.status_code == 200:
                                                response_json = response.json()
                                                if response_json.get("update") == True:
                                                    print(f"OTP for {phone_number} updated successfully via {BATCH_ENDPOINT_1}.")
                                                    # Delete the email after processing
                                                    mail.store(num, '+FLAGS', '\\Deleted')
                                                    mail.expunge()
                                                else:
                                                    print(f"Error from {BATCH_ENDPOINT_1}: {response_json.get('message')}. Trying fallback URL.")
                                                    # If the first URL fails, try the second URL
                                                    url_2 = f"{BATCH_ENDPOINT_2}&phone={phone_number}&otp={otp}"
                                                    print(f"Sending OTP request to fallback URL: {url_2}")
                                                    response = requests.get(url_2)

                                                    if response.status_code == 200:
                                                        response_json = response.json()
                                                        if response_json.get("update") == True:
                                                            print(f"OTP for {phone_number} updated successfully via {BATCH_ENDPOINT_2}.")
                                                            # Delete the email after processing
                                                            mail.store(num, '+FLAGS', '\\Deleted')
                                                            mail.expunge()
                                                        else:
                                                            print(f"Error from {BATCH_ENDPOINT_2}: {response_json.get('message')}")
                                                    else:
                                                        print(f"Failed to update OTP for {phone_number} from both URLs. HTTP status code: {response.status_code}")
                                        else:
                                            print("OTP not found in the email body.")
                                    else:
                                        print(f"Invalid sender: {sender}. Deleting email.")
                                        mail.store(num, '+FLAGS', '\\Deleted')
                                        mail.expunge()
                                else:
                                    print(f"Invalid subject: {subject}. Deleting email.")
                                    mail.store(num, '+FLAGS', '\\Deleted')
                                    mail.expunge()
                    else:
                        print(f"Failed to fetch email {num}.")
                except Exception as e:
                    print(f"Error fetching email {num}: {e}")
        else:
            print("No unread emails found.")
    else:
        print("Search failed.")

    # Close connection
    mail.close()
    mail.logout()

if __name__ == "__main__":
    while True:
        check_inbox()

        # Get current UTC time and convert to Dhaka time (UTC+6)
        utc_now = datetime.datetime.utcnow()
        dhaka_now = utc_now + datetime.timedelta(hours=6)

        # Define time range in Dhaka time
        start_time = dhaka_now.replace(hour=13, minute=0, second=0, microsecond=0)
        #end_time = dhaka_now.replace(hour=24, minute=0, second=0, microsecond=0)
        end_time = (dhaka_now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        # Check if current Dhaka time is between 15:00:00 and 22:00:00
        if start_time <= dhaka_now <= end_time:
            sleep_interval = 5   # check every second
        else:
            sleep_interval = 10  # check every minute

        print(f"Current Dhaka time: {dhaka_now.time()} - Sleeping for {sleep_interval} seconds")
        time.sleep(sleep_interval)