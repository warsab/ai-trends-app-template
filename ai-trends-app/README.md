# AI Trends Dashboard - Template

A customizable AI-powered trends dashboard that generates personalized reports based on web-scraped content, features an intelligent chatbot, LinkedIn post generation, and YouTube video recommendations.

## 🌟 Features

- **Personalized AI Reports**: Generate custom AI trends reports based on user profiles and interests
- **Web Scraping**: Configurable web scraper to fetch articles from any newsletter or blog
- **Intelligent Chatbot**: AI assistant with real-time web search capabilities
- **LinkedIn Post Generator**: Create engaging LinkedIn posts from reports or custom topics
- **YouTube Recommendations**: Get personalized video recommendations based on your interests
- **AI Leaderboard**: Visualize the latest AI model performance benchmarks
- **User Profiles**: YAML-based user profiles for personalization
- **Multi-user Support**: Secure authentication with bcrypt password hashing

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Customization](#customization)
- [Project Structure](#project-structure)
- [API Keys](#api-keys)
- [Adding Users](#adding-users)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- API Keys (see [API Keys](#api-keys) section)

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/fw-ai-trends.git
cd fw-ai-trends
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file and configure it:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys (see [Configuration](#configuration) section below).

## ⚙️ Configuration

### Required Configuration

Edit your `.env` file with the following:
```bash
# OpenAI API (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration (REQUIRED - Generate a secure key!)
SECRET_KEY=your_secret_key_here_generate_with_secrets_token_hex_32

# Web Scraper Configuration (REQUIRED)
SCRAPER_BASE_URL=https://yournewsletter.beehiiv.com/

# Optional APIs (for enhanced features)
TAVILY_API_KEY=your_tavily_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here

# Model Configuration (Optional)
GPT_MODEL_STANDARD=gpt-3.5-turbo
GPT_MODEL_ADVANCED=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=2000

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

### Generating a Secure Secret Key

Run this command to generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it into your `.env` file.

## 🚀 Usage

### Running the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Default Login

- **Username**: `demo`
- **Password**: `demo123`

**⚠️ IMPORTANT**: Change this password in production! See [Adding Users](#adding-users) section.

### Using the Dashboard

1. **Generate Report**: Click "Generate Report" to create a personalized AI trends report
2. **Chat with AI**: Click "Chat with AI Assistant" to ask questions about AI trends
3. **YouTube Videos**: Click "Get Videos" for personalized video recommendations
4. **LinkedIn Posts**: Click "LinkedIn Post" to generate social media content
5. **AI Leaderboard**: Click "AI Leaderboard" to view model performance rankings

## 🎨 Customization

### 1. Configure Your Web Scraper

Edit your `.env` file to scrape from your preferred source:
```bash
SCRAPER_BASE_URL=https://your-newsletter-or-blog.com/
```

The scraper (`scrapers/ws_tool.py`) is designed for Beehiiv-style layouts but can be adapted for other sites.

### 2. Customize User Profiles

User profiles are stored as YAML files in `data/users/`. To create a new user profile:

**Create `data/users/username.yaml`:**
```yaml
name: Your Name
email: your.email@example.com
job_title: Your Job Title
interests: "Describe your professional interests and what you want to track in AI..."
tags:
  - tag1
  - tag2
  - tag3
```

### 3. Customize Branding

**Update Dashboard Title:**
Edit `static/js/main.js` line 2:
```javascript
// Change dashboard title/branding
```

**Update Colors:**
Edit `templates/base.html` Tailwind configuration:
```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#eff6ff',   // Customize these
                    500: '#3b82f6',
                    600: '#2563eb',
                    700: '#1d4ed8'
                }
            }
        }
    }
}
```

### 4. Add Custom Scrapers

Create new scraper files in `scrapers/` folder and add them to `backend/ai_agents.py` in the `run_scrapers()` method.

## 📁 Project Structure
```
fw-ai-trends/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
│
├── backend/                   # Backend modules
│   ├── ai_agents.py          # AI pipeline and report generation
│   ├── user_manager.py       # User authentication and profiles
│   └── utils.py              # Utility functions
│
├── scrapers/                  # Web scraping tools
│   ├── ws_tool.py            # Generic web scraper
│   └── llm_leaderboard.py    # AI leaderboard scraper
│
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── login.html            # Login page
│   └── dashboard.html        # Main dashboard
│
├── static/                    # Static assets
│   ├── js/
│   │   └── main.js           # JavaScript functions
│   └── images/               # Images and logos
│
├── data/                      # Data storage
│   ├── users/                # User profile YAML files
│   ├── reports/              # Generated reports
│   ├── scraped/              # Scraped data
│   └── backups/              # Backup files
│
└── logs/                      # Application logs
```

## 🔑 API Keys

### Required APIs

#### 1. OpenAI API (Required)
- **Purpose**: Powers AI report generation, chatbot, and content creation
- **Get it**: https://platform.openai.com/api-keys
- **Pricing**: Pay-as-you-go (GPT-3.5-turbo is cheaper, GPT-4 is more capable)

### Optional APIs

#### 2. Tavily API (Optional)
- **Purpose**: Real-time web search for chatbot
- **Get it**: https://tavily.com/
- **Benefits**: Enables chatbot to answer questions about latest news
- **Without it**: Chatbot still works but without real-time search

#### 3. YouTube API (Optional)
- **Purpose**: Personalized video recommendations
- **Get it**: https://console.cloud.google.com/apis/library/youtube.googleapis.com
- **Benefits**: Get AI video recommendations
- **Without it**: Video recommendation feature won't work

## 👥 Adding Users

### Step 1: Generate Password Hash
```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"
```

### Step 2: Add User to config.py

Edit `config.py` and add to the USERS dictionary:
```python
USERS = {
    'demo': {
        'password': '$2b$12$...',
        'profile': 'demo.yaml'
    },
    'newuser': {
        'password': '$2b$12$...your_generated_hash...',
        'profile': 'newuser.yaml'
    }
}
```

### Step 3: Create User Profile

Create `data/users/newuser.yaml`:
```yaml
name: New User
email: newuser@example.com
job_title: Software Engineer
interests: "I'm interested in machine learning and AI development..."
tags:
  - machine_learning
  - ai_development
  - python
```

### Step 4: Restart Application
```bash
# Stop the app (Ctrl+C) and restart
python app.py
```

## 🌐 Deployment

### Environment Variables for Production
```bash
DEBUG=False
SECRET_KEY=your_production_secret_key
# Add all API keys
```

### Deployment Options

#### Option 1: Render.com (Recommended for beginners)

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Add environment variables in Render dashboard
5. Deploy!

See `render.yaml` for configuration.

#### Option 2: Heroku
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
git push heroku main
```

#### Option 3: AWS/GCP/Azure

Deploy as a containerized application using Docker or deploy directly to EC2/Compute Engine/App Service.

### Production Checklist

- [ ] Change SECRET_KEY from default
- [ ] Set DEBUG=False
- [ ] Remove or change demo user credentials
- [ ] Configure proper logging
- [ ] Set up HTTPS/SSL
- [ ] Configure rate limiting
- [ ] Set up monitoring
- [ ] Regular backups of data/ folder

## 🔍 Troubleshooting

### Common Issues

#### "OPENAI_API_KEY not set"
- Ensure `.env` file exists in the root directory
- Check that `OPENAI_API_KEY=sk-...` is properly set (no quotes needed)
- Restart the application after changing `.env`

#### "Module not found" errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version (requires 3.8+)

#### Web scraper not working
- Verify `SCRAPER_BASE_URL` is set in `.env`
- Check if the target website structure matches Beehiiv layout
- Review logs in `logs/` folder for detailed error messages

#### Login fails
- Verify password hash was generated correctly
- Check that user profile YAML file exists in `data/users/`
- Ensure username in `config.py` matches profile filename

#### Reports not generating
- Check OpenAI API key is valid and has credits
- Verify scraped data exists in `data/scraped/`
- Review logs for API errors or rate limiting

### Getting Help

1. Check the logs in `logs/app.log`
2. Enable debug mode temporarily: `DEBUG=True` in `.env`
3. Search existing issues on GitHub
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Log files (remove sensitive data)

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow existing code style and structure
- Add comments to complex functions
- Update README.md if adding new features
- Test with demo user before submitting PR

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask, LangChain, and OpenAI
- UI powered by Tailwind CSS
- Icons by Font Awesome
- Inspired by the need for personalized AI trend tracking

## 📞 Support

- **Issues**: https://github.com/yourusername/fw-ai-trends/issues
- **Discussions**: https://github.com/yourusername/fw-ai-trends/discussions

## 🔄 Updates

Check the [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

**Made with ❤️ for the AI community**

*Star ⭐ this repo if you find it useful!*
