# AskMate AI Telegram Bot

A simple, production‑ready Telegram assistant that answers questions, provides guidance, and helps with everyday topics – all without external APIs or AI services.

## Features

- 📋 **Main Menu** with four options: Ask a Question, Get Assistance, Find Information, General Chat.
- 🤖 **Built‑in knowledge** for categories like Telegram, social media, marketing, SEO, programming, business, and more.
- 🛠 **Assistance** tailored for bot setup, troubleshooting, and general guidance.
- 🔍 **Information lookup** – uses the same built‑in responses (no live web search).
- 💬 **General chat** – conversational interaction with the same logic.
- ↩️ **Back to Menu** button everywhere.
- 🔒 **Privacy‑first**: no database, no user data storage.

## Deployment on Railway

1. Fork/clone this repository to GitHub.
2. Create a new bot via [@BotFather](https://t.me/BotFather) and copy its token.
3. On Railway, create a new project from your GitHub repo.
4. Add the environment variable:
   - `TELEGRAM_BOT_TOKEN` = your bot token.
5. Railway will automatically build and run the bot using the `Procfile`.

## Local Development

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
