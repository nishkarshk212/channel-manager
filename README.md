# 🚀 Telegram Channel Management Bot

A powerful, modern, and production-ready Telegram bot for professional channel management. Built with Python and Pyrogram.

## ✨ Features

- **Multi-channel support**: Manage multiple channels from a single bot interface.
- **Advanced Post Management**: Upload text, photos, videos, and more with custom buttons.
- **Scheduling**: Plan your content in advance with the built-in scheduler.
- **Analytics**: Track channel growth and post performance.
- **Role System**: Owner, Admin, and Editor roles for team collaboration.
- **Modular Architecture**: Easy to extend and maintain.
- **Database Support**: MongoDB for persistent storage.
- **Docker Ready**: Easy deployment using Docker and Docker Compose.

## 🛠 Installation

### Prerequisites
- Python 3.10+
- MongoDB
- Telegram API ID and Hash (from [my.telegram.org](https://my.telegram.org))
- Bot Token (from [@BotFather](https://t.me/BotFather))

### Local Setup
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd channel_management
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

### Docker Deployment
```bash
docker-compose up -d --build
```

## 🚢 Deployment Guide

### VPS (Ubuntu/Debian)
1. Install Docker and Docker Compose.
2. Clone this repo and setup `.env`.
3. Run `docker-compose up -d`.

### Railway / Render
1. Connect your GitHub repository.
2. Add environment variables in the dashboard.
3. Deploy (Dockerfile will be detected automatically).

## 📂 Project Structure
- `handlers/`: Bot command and callback handlers.
- `database/`: MongoDB connection and CRUD operations.
- `services/`: Business logic (analytics, broadcast, post service).
- `utils/`: Helper functions and configuration.
- `middlewares/`: Authentication and permission checks.

## 🔒 Security Best Practices
- Keep your `.env` file secret.
- Only authorize trusted admins.
- Use the built-in role system to limit access.

## 📝 License
MIT
