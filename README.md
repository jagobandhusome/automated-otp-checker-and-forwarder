This script serves as an automated OTP processing system that:

Connects to an IMAP email server to monitor incoming messages

Identifies OTP emails from specific senders with predefined subjects

Extracts phone numbers and OTP codes using regex patterns

Automatically forwards extracted OTPs to configured API endpoints

Handles both direct emails and forwarded messages

Includes fallback mechanisms for reliable delivery

🚀 Features
Real-time Monitoring: Continuously checks for new unread emails

Smart Filtering: Identifies legitimate OTP emails while ignoring spam/confirmation messages

Dual Endpoint Support: Primary and fallback API endpoints for reliable delivery

Phone Number Extraction: Supports multiple email formats and forwarding scenarios

Time-based Optimization: Adjusts checking frequency based on time of day

Error Handling: Robust exception handling and logging

Auto-cleanup: Automatically deletes processed emails

🛠️ Technical Details
Technologies Used:

Python 3.x

IMAP protocol for email access

Regular expressions for data extraction

HTTP requests for API communication

DateTime for time-based operations

Key Components:

imaplib for secure email server connection

email library for parsing email content

re for pattern matching and data extraction

requests for HTTP API calls

Configurable time-based execution intervals

⚙️ Configuration
The script uses the following configurable parameters:

python
EMAIL = "your-email@domain.com"
PASSWORD = "your-password"
IMAP_SERVER = "mail.domain.com"
IMAP_PORT = 993
BATCH_ENDPOINT_1 = "https://api.example.com/primary-endpoint"
BATCH_ENDPOINT_2 = "https://api.example.com/fallback-endpoint"
📁 Project Structure
text
automatic_otp_checker/
├── automatic_OTP_Checker.py  # Main script
├── README.md                 # This file
└── requirements.txt          # Dependencies (if any)
🎯 Use Cases
Automated Verification Systems: Streamline OTP-based authentication workflows

Payment Processing: Automate financial transaction verifications

Account Management: Handle bulk account creation/verification

Testing Environments: Automated testing of OTP-dependent systems

⚠️ Security Notes
Ensure email credentials are stored securely

Use encrypted connections (IMAP over SSL)

Regularly update and monitor the system

Consider implementing additional authentication layers

🚀 Getting Started
Install required dependencies:

bash
pip install requests
Configure email and API endpoints in the script

Run the script:

bash
python automatic_OTP_Checker.py
🔧 Customization
The script can be easily modified to:

Support different email providers

Handle various OTP formats

Integrate with different API endpoints

Adjust processing logic based on specific requirements
