# Alex's Telegram Bot v2.0 - MEXC Verification Bot

🚀 **Reto de 50$ a 500$ con Cripto Trading**

## ✨ New Features v2.0

### 🎯 Smart UID Detection
- **Automatic Recognition**: Detects 8-digit UIDs in any message
- **Flexible Format**: Accepts "UID 12345678", "12345678", "Mi UID es 12345678"
- **Case Insensitive**: Works with "uid", "UID", "Uid"
- **No Command Required**: Users don't need to type /verify first

### 📱 Enhanced User Experience
- **Updated Welcome Message**: Focus on $50 to $500 challenge
- **Inline Keyboards**: Easy navigation with buttons
- **Smart Responses**: Contextual help and guidance
- **Error Handling**: Graceful failure with helpful messages

## 🚀 Quick Start

### Installation
```bash
# Extract the package
unzip alex_telegram_bot_v2_complete.zip
cd alex_telegram_bot_v2

# Install dependencies
pip install -r requirements.txt

# Start the bot
python main.py
```

### Docker Installation
```bash
# Build and run
docker build -t alex-telegram-bot .
docker run -d --name alex-bot alex-telegram-bot
```

## 📋 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and verification setup |
| `/verify` | Manual verification process |

## 🎯 User Flow

1. **User starts bot** → Receives welcome message
2. **User sends UID** → Smart detection activates
3. **Bot verifies UID** → Checks against MEXC API
4. **Success** → User gets VIP group access
5. **Failure** → User gets registration guidance

## 📊 Smart UID Detection Examples

✅ **Accepted Formats**:
- `12345678`
- `UID 12345678`
- `Mi UID es 12345678`
- `uid: 12345678`

❌ **Rejected Formats**:
- `1234567` (7 digits)
- `123456789` (9 digits)
- `abcd1234` (contains letters)

## 🔧 Configuration

All credentials are pre-configured:
- **Telegram Token**: 8016598513:AAFtYbJD6vOXpIH9t8wu_-nSfBJmSn2KQNk
- **MEXC API Key**: mx0vgl6Q1sImSUitga
- **MEXC Secret**: b79a8e0f6a4b4730a0e7e198e5b5e110
- **VIP Group**: https://t.me/+S4YxyCi0aEU3ZTA0

## 📞 Support

- **Developer**: @alex.worksout
- **Issues**: Check logs first, then contact Alex

---

🚀 **¡Únete al reto y transforma 50$ en 500$!** 🚀
