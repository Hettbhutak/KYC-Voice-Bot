#  KYC Voice Bot
A Python-based voice AI system for conducting KYC (Know Your Customer) verification through natural voice interaction. Built for Decentro's fintech platform to streamline customer onboarding.

##  Overview

This voice bot simulates a compliant KYC verification call where users provide their details through speech. The system validates inputs, handles errors gracefully, and generates structured JSON logs for backend integration.

##  Features

- **Speech Recognition**: Captures user responses using Google Speech Recognition
- **Text-to-Speech**: Natural voice prompts using pyttsx3
- **Input Validation**: 
  - Name: Alphabetic characters, minimum 2 characters
  - Phone: Exactly 10 digits
  - PAN: 10 alphanumeric (5 letters + 4 digits + 1 letter format)
  - Consent: Yes/No validation
- **Error Handling**: Up to 2 retry attempts per field with helpful error messages
- **Session Logging**: Complete JSON audit trail for compliance
- **Graceful Degradation**: Handles unclear speech, timeouts, and technical errors

##  Tech Stack

- **Python 3.8+**
- **SpeechRecognition**: For converting speech to text
- **pyttsx3**: For text-to-speech conversion (offline)
- **PyAudio**: For microphone access

##  Installation

### Prerequisites

**For macOS:**
```bash
# Install PortAudio (required for PyAudio)
brew install portaudio
```

**For Ubuntu/Debian:**
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev
```

**For Windows:**
PyAudio installation may require downloading a wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio).

### Install Python Dependencies

```bash
# Clone the repository
git clone https://github.com/Hettbhutak/KYC-Voice-Bot
cd kyc-voice-bot

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

##  Usage

### Running the Bot

```bash
python kyc_bot.py
```

### What to Expect

1. **Welcome Message**: Bot greets you and explains the process
2. **Name Collection**: "May I have your full name please?"
3. **Phone Collection**: "What is your 10-digit phone number?"
4. **PAN Collection**: "Please provide your PAN number..."
5. **Consent**: "Do you consent to this KYC verification?"
6. **Confirmation**: Bot reads back all details
7. **Completion**: Session saved to JSON file

### Sample Interaction

```
🤖 Bot: Welcome to Decentro KYC verification...
🎤 Listening...
👤 You said: John Doe

🤖 Bot: Thank you. What is your 10-digit phone number?
🎤 Listening...
👤 You said: 9876543210

🤖 Bot: Please provide your PAN number...
🎤 Listening...
👤 You said: ABCDE1234F

🤖 Bot: Do you consent to this KYC verification?
🎤 Listening...
👤 You said: yes

🤖 Bot: Thank you. Let me confirm your details...
✅ Session saved to: output/kyc_session_20250211_143052.json
```

## 📄 Output Format

The bot generates a JSON file in the `output/` directory with the following structure:

```json
{
  "session_id": "kyc_20250211_143052",
  "timestamp": "2025-02-11T14:30:52.123456",
  "user_data": {
    "name": "John Doe",
    "phone": "9876543210",
    "pan": "ABCDE1234F",
    "consent": true
  },
  "verification_status": "completed",
  "attempts": {
    "name": 1,
    "phone": 1,
    "pan": 2,
    "consent": 1
  }
}
```

### Status Values
- `completed`: All data collected successfully
- `consent_declined`: User declined consent
- `cancelled`: User interrupted the process
- `error`: Technical error occurred

##  Demo

Watch a 1-minute demonstration of the bot in action:
[Demo Video Link]([demo/demo_recording.mp4](https://youtu.be/5l8rSI74Eu8))

##  Project Structure

```
kyc-voice-bot/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── kyc_bot.py            # Main bot implementation
├── demo/                 # Demo recording
│   └── demo_recording.mp4
└── output/               # Generated JSON sessions
    └── sample_output.json
```

##  Code Architecture

### Main Components

1. **KYCVoiceBot Class**: Core bot logic
   - `speak()`: Text-to-speech output
   - `listen()`: Speech-to-text input
   - `validate_*()`: Input validation functions
   - `collect_field()`: Generic field collection with retry logic
   - `collect_kyc_data()`: Main orchestration flow
   - `save_session()`: JSON output generation

2. **Validation Rules**:
   - **Name**: Minimum 2 characters, alphabetic only
   - **Phone**: Exactly 10 digits
   - **PAN**: AAAAA9999A format (5 letters, 4 digits, 1 letter)
   - **Consent**: Must be explicit yes or no

3. **Error Handling**:
   - Timeout errors: "I didn't hear anything"
   - Unclear speech: "I didn't catch that clearly"
   - Invalid input: Field-specific error messages
   - Maximum 2 retry attempts per field

##  Known Limitations

1. **Microphone Quality**: Requires a working microphone; quality affects recognition accuracy
2. **Background Noise**: Best used in quiet environments
3. **Accent Variations**: Google Speech Recognition may have varying accuracy with different accents
4. **Internet Required**: Speech recognition uses Google's API (requires internet)
5. **TTS Voice**: Uses system default voice (quality varies by OS)

##  Future Enhancements

If given more time, these features could be added:

1. **Multi-language Support**: Support for regional languages
2. **Voice Authentication**: Biometric voice verification
3. **Document Upload**: Integration with document scanning
4. **Live Dashboard**: Real-time monitoring of KYC sessions
5. **Offline Mode**: Fully offline speech recognition
6. **OTP Verification**: Phone number verification via OTP
7. **Database Integration**: Store sessions in a database
8. **API Endpoints**: RESTful API for session management

##  Testing

### Manual Testing Checklist

- [ ] Valid inputs (happy path)
- [ ] Invalid name (numbers, special chars)
- [ ] Invalid phone (< 10 or > 10 digits)
- [ ] Invalid PAN (wrong format)
- [ ] Consent declined
- [ ] Unclear speech (test retry logic)
- [ ] Background noise handling
- [ ] Keyboard interrupt (Ctrl+C)

### Test Cases

```bash
# Test 1: Happy Path
Name: "John Doe"
Phone: "9876543210"
PAN: "ABCDE1234F"
Consent: "yes"
Expected: ✅ Session saved with status "completed"

# Test 2: Invalid PAN
Name: "Jane Smith"
Phone: "8765432109"
PAN: "123456" (invalid)
Expected: ❌ Retry prompt, then ask again

# Test 3: No Consent
Name: "Bob Johnson"
Phone: "7654321098"
PAN: "XYZAB5678C"
Consent: "no"
Expected: ❌ Session saved with status "consent_declined"
```

##  Contributing

This is an assignment submission, but suggestions are welcome!

##  License

This project is created for the Decentro AI SDE assignment.

##  Author

**Your Name**
- GitHub: [@Hettbhutak](https://github.com/Hettbhutak)
- Email: hetbhutak@gmail.com

##  Acknowledgments

- Decentro for the interesting assignment
- Google Speech Recognition API
- pyttsx3 community

---

**Note**: This is a prototype built in 2-3 hours as per assignment requirements. Production use would require additional security, scalability, and compliance features.
