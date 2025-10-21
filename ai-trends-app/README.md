# 🚀 Smart Trendz AI Dashboard

> AI-powered personalized news aggregation and content generation platform

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)

**Smart Trendz** is an intelligent dashboard that aggregates AI news from multiple sources, generates personalized reports, and creates shareable content tailored to your professional interests.

---

## ✨ Features

### 🎯 Core Functionality

- **📊 Personalized AI Reports** - Generate custom AI trend reports based on your job role and interests
- **🕷️ Automated Web Scraping** - Fetch latest news from OpenAI, Beehiiv AI Engineering, and The Batch newsletter
- **💬 AI Chatbot Assistant** - Interactive Q&A powered by GPT-4 with real-time web search via Tavily
- **📱 LinkedIn Post Generator** - Create professional posts from reports or custom topics
- **🎥 YouTube Recommendations** - Get personalized AI video suggestions based on your profile
- **🏆 AI Model Leaderboard** - LiveBench rankings with interactive visualizations

### 🎨 User Experience

- **Beautiful Glass Morphism UI** - Modern neon-themed interface with smooth animations
- **Multi-User Support** - Individual profiles with customized interests and tags
- **Session Management** - Secure authentication with Flask sessions
- **Real-time Notifications** - Toast notifications and loading states
- **Responsive Design** - Works seamlessly on desktop and mobile

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.0.0
- **Language:** Python 3.11+
- **AI/ML:** OpenAI GPT-4, GPT-3.5-turbo, LangChain
- **Search:** Tavily API for real-time web search
- **APIs:** YouTube Data API v3

### Frontend
- **Styling:** Tailwind CSS
- **JavaScript:** Vanilla JS (ES6+)
- **Icons:** Font Awesome 6.4.0

### Data & Storage
- **User Data:** YAML files
- **Reports:** JSON storage
- **Sessions:** Flask-Session (filesystem)
- **Scraped Data:** JSON with automatic backups

### Web Scraping
- **Libraries:** BeautifulSoup4, Requests, lxml
- **Targets:** OpenAI News, Beehiiv, The Batch Newsletter

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- API Keys:
  - OpenAI API key
  - Tavily API key
  - YouTube Data API key

### Quick Start

1. **Clone the repository**
```bash
