# GermanBuddy

GermanBuddy is an AI-powered language learning assistant designed to help users practice German through interactive conversations, grammar checks, vocabulary definitions, pronunciation assistance, and translations into English and Bengali (Bangla). It features a Flask backend for AI logic and a React frontend for a modern, responsive chat interface.

## Features

- **Conversational Practice**: Chat in German with adaptive difficulty (beginner, intermediate, advanced).
- **Grammar Checking**: Validate German text using LanguageTool.
- **Vocabulary Definitions**: Look up German word meanings (mock dictionary).
- **Pronunciation**: Generate and play audio for German text.
- **Multilingual Translations**: Translate German responses to English and Bengali.
- **Web Interface**: React-based chat UI with real-time interaction.

## Tech Stack

### Backend
- **Python 3.8+**: Core language.
- **Flask**: Web framework for API and serving.
- **LangGraph**: State machine for agent routing.
- **LangChain**: LLM integration.
- **deep-translator**: Translation engine.
- **gTTS**: Text-to-speech.
- **LanguageTool**: Grammar checking.
- **Logging**: Debugging and monitoring.

### Frontend
- **React**: JavaScript library for UI.
- **Node.js & npm**: For React development.
- **CSS**: Basic styling.
- **Fetch API**: Communication with backend.

## Prerequisites

- **Python 3.8+**: For backend (`python --version`).
- **Node.js 18+ & npm**: For frontend (`node --version`, `npm --version`).
- **Git**: For cloning (optional).
- **Web Browser**: For testing.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/GermanBuddy.git
cd GermanBuddy