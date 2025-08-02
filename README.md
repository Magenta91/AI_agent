# Outreach Assistant

An automated Python tool for personalized lead outreach via email and WhatsApp using Google Sheets, Gemini AI, Gmail SMTP, and Twilio.

## Features

- 📊 Read lead data from Google Sheets
- 🤖 Generate personalized messages using Gemini AI (using Gemini 1.5 Flash)
- 📧 Send emails via Gmail SMTP
- 📱 Send WhatsApp messages via Twilio
- ✅ Automatic status updates in Google Sheets
- 🧪 Test mode for safe testing
- 🔄 Retry failed leads functionality
- 📝 Comprehensive logging
- 🌍 Smart phone number formatting (supports Indian and US numbers)
- 🛠️ Utility scripts for debugging and management

## Requirements

- Python 3.10+
- Google Cloud Service Account with Sheets API access
- Gemini API key
- Gmail account with App Password
- Twilio account with WhatsApp API access

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd outreach_assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual credentials (see Configuration section below).

## Configuration

### 1. Google Sheets Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Google Sheets API

2. **Create Service Account:**
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Download the JSON credentials file
   - Place it in your project directory

3. **Prepare your Google Sheet:**
   - Create a Google Sheet with columns: Name, Contact, Interest, Region, Status
   - Share the sheet with your service account email (found in the JSON file)
   - Copy the Sheet ID from the URL

### 2. Gemini API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Add it to your `.env` file

### 3. Gmail Setup

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password:**
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
   - Use this password in `.env` file

### 4. Twilio WhatsApp Setup

1. **Create Twilio Account:**
   - Sign up at [Twilio](https://www.twilio.com/)
   - Get your Account SID and Auth Token

2. **Set up WhatsApp Sandbox:**
   - Go to Console > Messaging > Try it out > Send a WhatsApp message
   - Follow the sandbox setup instructions
   - Note your WhatsApp number (format: `whatsapp:+1234567890`)

### 5. Environment Variables

Update your `.env` file:

```env
# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS=path/to/your/credentials.json
SPREADSHEET_ID=your_google_sheet_id_here

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Gmail SMTP Configuration
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password

# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

## Usage

### Basic Commands

1. **Test all connections:**
   ```bash
   python main.py --test-connections
   ```

2. **Run in test mode (no actual sending):**
   ```bash
   python main.py --test
   ```

3. **Run the actual campaign:**
   ```bash
   python main.py
   ```

4. **Retry failed leads:**
   ```bash
   python main.py --retry-failed
   ```

5. **Specify different sheet name:**
   ```bash
   python main.py --sheet-name "Leads2024"
   ```

### Google Sheet Format

Your Google Sheet should have these columns (in order):

| Name | Contact | Interest | Region | Status |
|------|---------|----------|---------|---------|
| John Doe | john@example.com | Web Development | New York | Pending |
| Jane Smith | +1234567890 | Mobile Apps | California | Pending |

**Contact formats supported:**
- Email: `user@example.com`
- Phone: `+1234567890`, `(123) 456-7890`, `123-456-7890`
- Indian mobile: `9523860283` (automatically formatted as `+919523860283`)
- US mobile: `2345678901` (automatically formatted as `+12345678901`)

**Status values:**
- `Pending`: Ready to be processed
- `Sent`: Successfully sent
- `Error`: Failed to send

### Message Generation

The tool uses Gemini AI to generate personalized messages with this template:

- Greets the lead by name
- Mentions their interest and region naturally
- Keeps messages under 80 words
- Ends with a clear call to action

## Project Structure

```
outreach_assistant/
├── main.py                 # Entry point and orchestration
├── google_sheets.py        # Google Sheets integration
├── message_generator.py    # Gemini AI message generation (Gemini 1.5 Flash)
├── sender.py              # Email and WhatsApp sending with smart phone formatting
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── .env.example          # Environment variables template
├── README.md             # This file
├── check_sheets.py        # Utility: Check available sheets and data
├── reset_status.py        # Utility: Reset lead status for testing
└── check_twilio.py        # Utility: Check Twilio WhatsApp status
```

## Logging

The application logs to both console and `outreach_assistant.log` file:

- ✅ Success messages in green
- ❌ Error messages in red
- ℹ️ Info messages for tracking progress

## Error Handling

- **Invalid contact formats**: Logged as errors, status set to "Error"
- **API failures**: Logged with details, status set to "Error"
- **Network issues**: Retryable by resetting status to "Pending"
- **Missing data**: Skipped with warning logs

## Security Best Practices

- Never commit `.env` file to version control
- Use App Passwords instead of regular Gmail passwords
- Regularly rotate API keys
- Keep service account JSON files secure
- Use environment variables for all sensitive data

## Utility Scripts

The project includes several utility scripts for debugging and management:

### check_sheets.py
Check available Google Sheets and preview data:
```bash
python check_sheets.py
```
This will show:
- Available sheet names and IDs
- Sample data from the first sheet
- Helps identify correct sheet name for configuration

### reset_status.py
Reset a specific lead's status back to "Pending" for testing:
```bash
python reset_status.py
```
Useful for:
- Testing message generation again
- Retrying failed sends
- Development and debugging

### check_twilio.py
Check Twilio WhatsApp sandbox status and recent messages:
```bash
python check_twilio.py
```
Shows:
- Account status
- Recent WhatsApp messages
- Sandbox setup instructions

## Troubleshooting

### Common Issues

1. **"No module named 'google'"**
   ```bash
   pip install --upgrade google-api-python-client google-auth
   ```

2. **Gmail authentication failed**
   - Ensure 2FA is enabled
   - Use App Password, not regular password
   - Check Gmail security settings

3. **Google Sheets permission denied**
   - Share sheet with service account email
   - Check service account has Sheets API enabled
   - Use `python check_sheets.py` to verify connection

4. **Wrong sheet name error**
   - Run `python check_sheets.py` to see available sheet names
   - Update default sheet name in code or use `--sheet-name` parameter

5. **Twilio WhatsApp errors**
   - Verify sandbox setup is complete
   - Check phone number format (use `python check_twilio.py`)
   - Ensure recipients have joined the WhatsApp sandbox
   - For sandbox: Send "join <keyword>" to +1 415 523 8886

6. **Phone number formatting issues**
   - Indian numbers (10 digits starting with 6,7,8,9): Auto-formatted as +91xxxxxxxxxx
   - US numbers (10 digits): Auto-formatted as +1xxxxxxxxxx
   - Numbers with country code: Use as-is with + prefix

7. **Gemini API errors**
   - Verify API key is correct
   - Check API quotas and billing
   - Ensure Gemini API is enabled
   - Model updated to use 'gemini-1.5-flash'

8. **WhatsApp messages not received**
   - Check if recipient joined Twilio sandbox
   - Verify phone number format in logs
   - Use `python check_twilio.py` to see message status

### Debug Mode

For detailed debugging, modify the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Implementation Notes

### Key Updates Made During Development

1. **Gemini API Model Update**: Changed from `gemini-pro` to `gemini-1.5-flash` for better performance and availability.

2. **Phone Number Formatting Fix**: Implemented smart formatting logic:
   - Detects Indian mobile numbers (10 digits starting with 6,7,8,9)
   - Automatically adds appropriate country codes (+91 for India, +1 for US)
   - Handles various input formats gracefully

3. **Sheet Name Detection**: Added utility to detect actual sheet names instead of assuming "Sheet1".

4. **Enhanced Error Handling**: Improved logging and error messages for better debugging.

5. **Unicode Logging Fix**: Resolved Windows console encoding issues with success/error symbols.

### Configuration Files Created

- `.env`: Contains all API keys and configuration
- `mcp1-467108-178a63ae2167.json`: Google service account credentials
- `outreach_leads`: Google Sheet with lead data

### Successful Test Campaign Results

✅ **Email Campaign**: Successfully sent personalized email to Gmail address  
✅ **WhatsApp Campaign**: Successfully sent personalized WhatsApp message to Indian mobile number  
✅ **Status Updates**: Automatically updated Google Sheets with "Sent" status  
✅ **Message Generation**: AI-generated personalized messages mentioning name, interest, and region  

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `outreach_assistant.log`
3. Use utility scripts (`check_sheets.py`, `check_twilio.py`) for debugging
4. Create an issue in the repository

## Testing and Deployment Process

### Step-by-Step Testing

1. **Test all connections first:**
   ```bash
   python main.py --test-connections
   ```
   This verifies:
   - Google Sheets API connection
   - Gemini AI API connection
   - Gmail SMTP connection
   - Twilio WhatsApp API connection

2. **Run in test mode (safe):**
   ```bash
   python main.py --test
   ```
   This will:
   - Generate personalized messages
   - Show what would be sent
   - Not actually send messages
   - Not update Google Sheets

3. **Check your sheet data:**
   ```bash
   python check_sheets.py
   ```
   Verify your leads are properly formatted

4. **Run the actual campaign:**
   ```bash
   python main.py
   ```
   This will:
   - Send real messages
   - Update Google Sheets status
   - Log all activities

5. **Monitor and retry if needed:**
   ```bash
   python main.py --retry-failed
   ```

### Example Test Results

When testing, you should see output like:
```
SUCCESS: Google Sheets: Connected successfully (2 leads found)
SUCCESS: Gemini API: Connected successfully  
SUCCESS: Gmail SMTP: Connected successfully
SUCCESS: Twilio WhatsApp: Connected successfully
```

### Phone Number Formatting Examples

The system automatically formats phone numbers:
- `9523860283` → `+919523860283` (Indian mobile)
- `2345678901` → `+12345678901` (US mobile)
- `919523860283` → `+919523860283` (Indian with country code)
- `+919523860283` → `+919523860283` (already formatted)

---

**⚠️ Important**: Always test with a small batch of leads first and use `--test` mode to verify everything works correctly before running large campaigns.