# ============================================================================
# AI AGENTS PIPELINE
# ============================================================================
# 
# This module handles all AI-powered features of the application:
# - Report generation from scraped newsletter data
# - Chatbot interactions with web search capability
# - LinkedIn post generation
# - YouTube video recommendations
# - Content processing and personalization
#
# KEY COMPONENTS:
# - LangChain integration for structured AI interactions
# - OpenAI GPT models for content generation
# - Tavily API for real-time web search
# - YouTube API for video recommendations
#
# CONFIGURATION:
# - Requires OPENAI_API_KEY in .env (required)
# - Requires TAVILY_API_KEY in .env (optional, for web search)
# - Requires YOUTUBE_API_KEY in .env (optional, for video recommendations)
# ============================================================================

import openai
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import logging
import json
import os
import sys
from datetime import datetime
import subprocess
from tavily import TavilyClient
import requests  
from urllib.parse import urlencode

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from backend.utils import log_performance, retry_on_failure

logger = logging.getLogger(__name__)

class AIAgentsPipeline:
    """
    Handles all AI agent interactions using LangChain and OpenAI.
    
    This is the core AI engine that powers:
    - Personalized report generation
    - Interactive chatbot
    - LinkedIn post creation
    - YouTube video recommendations
    """
    
    def __init__(self):
        """
        Initialize the AI pipeline with necessary API clients and models.
        
        Raises:
            ValueError: If OPENAI_API_KEY is not configured
        """
        # Check if API key is set
        if not Config.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not set in environment variables")
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file")
        
        # Initialize OpenAI
        openai.api_key = Config.OPENAI_API_KEY
        
        # Determine base directory for file paths
        self.base_dir = self._get_base_dir()
        
        # Initialize LangChain models
        # Standard model: Faster and cheaper, used for most tasks
        self.standard_model = ChatOpenAI(
            model=Config.GPT_MODEL_STANDARD,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            api_key=Config.OPENAI_API_KEY
        )
        
        # Advanced model: More capable, used for complex tasks
        self.advanced_model = ChatOpenAI(
            model=Config.GPT_MODEL_ADVANCED,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            api_key=Config.OPENAI_API_KEY
        )
        
        # Initialize Tavily client for web search (optional)
        self.tavily_client = None
        if Config.TAVILY_API_KEY:
            try:
                self.tavily_client = TavilyClient(api_key=Config.TAVILY_API_KEY)
                logger.info("Tavily search client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily: {str(e)}")
        else:
            logger.warning("TAVILY_API_KEY not set, web search will be disabled")
        
        logger.info("AI Agents Pipeline initialized")
    
    def _get_base_dir(self):
        """
        Get the base directory for the application.
        
        This method determines the correct base directory regardless of where
        the script is run from, ensuring file paths work correctly.
        
        Returns:
            str: Absolute path to the application base directory
        """
        # Get the directory where this file (ai_agents.py) is located
        # This is more reliable than using os.getcwd()
        this_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(this_file)
        app_dir = os.path.dirname(backend_dir)
        
        print(f"[DEBUG] AI Agents file location: {this_file}")
        print(f"[DEBUG] Backend directory: {backend_dir}")
        print(f"[DEBUG] App directory: {app_dir}")
        
        return app_dir
    
    # ========================================================================
    # WEB SCRAPING
    # ========================================================================
    
    def run_scrapers(self):
        """
        Run web scraper to fetch fresh data before generating report.
        
        This method executes the ws_tool.py scraper which fetches articles from
        the URL configured in SCRAPER_BASE_URL environment variable.
        
        CUSTOMIZATION:
        - Set SCRAPER_BASE_URL in your .env file to scrape your chosen newsletter/blog
        - Modify ws_tool.py if you need different scraping logic
        
        Returns:
            dict: Status of scraper execution {'Newsletter Articles': 'success/failed/...'}
        """
        print("\n" + "="*80)
        print("🕷️  RUNNING WEB SCRAPER - FETCHING FRESH DATA")
        print("="*80)
        print(f"[DEBUG] Base directory: {self.base_dir}")
        print(f"[DEBUG] Absolute base: {os.path.abspath(self.base_dir)}")
        
        # Single scraper configuration
        scraper_name = 'Newsletter Articles'
        scraper_path = 'scrapers/ws_tool.py'
        
        results = {}
        
        print(f"\n📡 Running {scraper_name} scraper...")
        try:
            # Get full path to scraper
            full_path = os.path.join(self.base_dir, scraper_path)
            abs_path = os.path.abspath(full_path)
            
            print(f"[DEBUG] Full path: {full_path}")
            print(f"[DEBUG] Absolute path: {abs_path}")
            print(f"[DEBUG] File exists: {os.path.exists(abs_path)}")
            
            if not os.path.exists(abs_path):
                print(f"❌ Scraper file not found at: {abs_path}")
                print(f"⚠️  Please ensure ws_tool.py exists in the scrapers folder")
                print(f"⚠️  And configure SCRAPER_BASE_URL in your .env file")
                results[scraper_name] = 'not_found'
            else:
                # Run the scraper as a subprocess
                result = subprocess.run(
                    [sys.executable, abs_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=os.path.abspath(self.base_dir),
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
                )
                
                if result.returncode == 0:
                    print(f"✅ {scraper_name} scraper completed successfully")
                    results[scraper_name] = 'success'
                else:
                    print(f"⚠️ {scraper_name} scraper failed with error:")
                    print(result.stderr[:500])
                    results[scraper_name] = 'failed'
                    
        except subprocess.TimeoutExpired:
            print(f"⚠️ {scraper_name} scraper timed out")
            results[scraper_name] = 'timeout'
        except Exception as e:
            print(f"⚠️ Error running {scraper_name} scraper: {str(e)}")
            results[scraper_name] = 'error'
        
        print("\n" + "="*80)
        print("📊 SCRAPING SUMMARY")
        print("="*80)
        for scraper_name, status in results.items():
            status_icon = "✅" if status == 'success' else "⚠️"
            print(f"{status_icon} {scraper_name}: {status}")
        print("="*80 + "\n")
        
        return results
    
    def load_json_file(self, filename):
        """
        Load JSON file from data/scraped directory.
        
        Args:
            filename (str): Name of the JSON file to load
            
        Returns:
            dict/list: Parsed JSON data, or None if file not found/invalid
        """
        filepath = os.path.join(self.base_dir, 'data', 'scraped', filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded {filename}")
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {filename}: {str(e)}")
            return None
    
    # ========================================================================
    # CONTENT PROCESSING
    # ========================================================================
    
    @log_performance
    @retry_on_failure(max_retries=2)
    def process_newsletter_articles(self, articles, source_name, user_profile):
        """
        Process newsletter articles (title + URL only).
        Filter for relevance and provide brief commentary.
        
        This works with any newsletter/blog that provides article titles and URLs.
        The AI analyzes each article and determines which ones are relevant to
        the user's profile and interests.
        
        Args:
            articles (list): List of article dictionaries with 'title' and 'article_url'
            source_name (str): Name of the source (e.g., "AI Newsletter")
            user_profile (dict): User profile with interests and tags
            
        Returns:
            str: Markdown-formatted analysis of relevant articles
        """
        if not articles:
            return None
        
        # Prepare articles data for AI (limit to avoid token limits)
        articles_text = "\n\n".join([
            f"Title: {article.get('title', 'No title')}\nURL: {article.get('article_url', 'No URL')}"
            for article in articles[:20]  # Limit to first 20
        ])
        
        system_prompt = f"""You are an AI content curator. Your job is to review article titles and URLs from {source_name} 
        and identify which ones would be most relevant and interesting to the user based on their profile.

        For each relevant article:
        1. Include the title and URL
        2. Add a brief 1-2 sentence commentary explaining why it's relevant
        3. Be enthusiastic but professional

        Only include articles that match the user's interests. If an article isn't relevant, skip it.
        
        Format your response in markdown with clear sections."""
        
        human_prompt = f"""User Profile:
        Name: {user_profile['name']}
        Job Title: {user_profile['job_title']}
        Interests: {user_profile['interests']}
        Tags: {', '.join(user_profile['tags'])}

        Articles to review:
        {articles_text}

        Please analyze these articles and return only the ones relevant to this user. 
        For each relevant article, provide the title, URL, and a brief comment on why it's interesting."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.standard_model.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error processing {source_name} articles: {str(e)}")
            raise
    
    # ========================================================================
    # WEB SEARCH
    # ========================================================================
    
    def search_web(self, query, max_results=5):
        """
        Search the web using Tavily API for real-time information.
        
        This is used to supplement scraped data with the latest news and trends.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return (default: 5)
            
        Returns:
            list: List of search results with title, content, and URL
                  Returns empty list if Tavily is not configured or search fails
        """
        if not self.tavily_client:
            logger.warning("Tavily client not initialized, cannot search web")
            return []
        
        try:
            logger.info(f"Searching web for: {query}")
            
            # Perform search
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"  # Use "advanced" for more thorough search
            )
            
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', 'No title'),
                    'content': result.get('content', 'No content'),
                    'url': result.get('url', 'No URL')
                })
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching web: {str(e)}")
            return []
    
    # ========================================================================
    # CHATBOT
    # ========================================================================
    
    @log_performance
    @retry_on_failure(max_retries=2)
    def chat_with_user(self, user_message, user_profile, conversation_history=None):
        """
        Chat with user about AI trends, personalized to their profile.
        Uses web search via Tavily API when user asks for latest/recent information.
        
        The chatbot automatically detects when users are asking for current information
        and performs real-time web searches to provide up-to-date answers.
        
        Args:
            user_message (str): The user's message
            user_profile (dict): User profile dictionary
            conversation_history (list): Previous messages [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            str: AI response as string
        """
        if conversation_history is None:
            conversation_history = []
        
        # Check if user is asking for latest/recent news (trigger web search)
        search_keywords = [
            'latest', 'recent', 'newest', 'current', 'today', 
            'this week', 'breaking', 'news', 'what\'s new', 
            'updates', 'happening', 'announcement', 'released'
        ]
        should_search_web = any(keyword in user_message.lower() for keyword in search_keywords)
        
        web_search_context = ""
        
        # Perform web search if needed
        if should_search_web and self.tavily_client:
            logger.info("Performing web search for user query...")
            
            # Create search query based on user message
            search_query = f"AI artificial intelligence {user_message}"
            web_results = self.search_web(search_query, max_results=5)
            
            if web_results:
                web_search_context = "\n**Live Web Search Results:**\n\n"
                for i, result in enumerate(web_results, 1):
                    web_search_context += f"{i}. **{result['title']}**\n"
                    web_search_context += f"   {result['content'][:250]}...\n"
                    web_search_context += f"   Source: {result['url']}\n\n"
                
                logger.info(f"Found {len(web_results)} web results to include in response")
            else:
                logger.warning("Web search returned no results")
        elif should_search_web and not self.tavily_client:
            logger.warning("User asked for latest news but Tavily client not available")
        
        # Determine tone based on user's job title
        job_title = user_profile.get('job_title', '').lower()
        
        if 'engineer' in job_title or 'developer' in job_title:
            tone = "technical and precise, with detailed explanations and code examples when relevant"
        elif 'manager' in job_title or 'executive' in job_title or 'ceo' in job_title:
            tone = "strategic and business-focused, emphasizing impact and opportunities"
        elif 'researcher' in job_title or 'scientist' in job_title:
            tone = "academic and thorough, with focus on methodologies and findings"
        elif 'designer' in job_title or 'product' in job_title:
            tone = "user-focused and practical, emphasizing applications and experiences"
        else:
            tone = "friendly and conversational, balancing accessibility with depth"
        
        # Build system prompt
        system_prompt = f"""You are an AI assistant specialized in artificial intelligence trends, news, and technology.
You're chatting with {user_profile['name']}, who works as a {user_profile['job_title']}.

**User Profile:**
- Name: {user_profile['name']}
- Job Title: {user_profile['job_title']}
- Interests: {user_profile['interests']}
- Focus Areas: {', '.join(user_profile['tags'])}

**Your Personality and Communication Style:**
- Use a {tone} tone
- Be enthusiastic about AI developments 🤖
- Personalize responses based on their role and interests
- Be conversational but informative
- Use emojis sparingly and appropriately (🤖 🚀 💡 ✨ 📊)
- Keep responses concise (under 250 words) unless asked for more detail

**Your Capabilities:**
- Answer questions about AI, machine learning, and technology trends
- Search the web in real-time when asked about latest/recent news
- Provide insights tailored to the user's professional background
- Explain complex AI concepts in accessible ways
- Recommend resources and articles when relevant

{web_search_context}

**Important Instructions:**
- If web search results are provided above, use them as your primary source
- Always cite sources by mentioning article titles and providing URLs
- If asked about something you don't have current information on, offer to search for it
- Be honest about the limits of your knowledge (knowledge cutoff: early 2024)
- For latest news queries, prioritize the web search results above
- Format URLs as clickable links in your response"""

        # Build messages for API
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history (last 6 messages for context)
        for msg in conversation_history[-6:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        try:
            # Use standard model for chat (faster responses)
            response = self.standard_model.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise

    # ========================================================================
    # LINKEDIN POST GENERATION
    # ========================================================================

    @log_performance
    @retry_on_failure(max_retries=2)
    def generate_linkedin_post_from_report(self, report_content, user_profile):
        """
        Generate a LinkedIn post from an existing report.
        
        Takes the key insights from a generated report and transforms them into
        an engaging, professional LinkedIn post with the user's voice.
        
        Args:
            report_content (str): The markdown report content
            user_profile (dict): User profile dictionary
            
        Returns:
            str: LinkedIn post text with formatting and hashtags
        """
        system_prompt = """You are a professional LinkedIn content creator specializing in AI and technology.
Your job is to create engaging, informative LinkedIn posts that drive engagement.

**Post Requirements:**
- Length: Approximately 300 words (2-3 short paragraphs)
- Style: Semi-casual, professional yet approachable
- Use emojis strategically (🤖 💡 🚀 ✨ 📊 🎯) - 3-5 total
- Include 5-8 relevant hashtags at the end
- Start with a hook that grabs attention
- End with a call-to-action or engaging question
- Use line breaks for readability
- Write in first person when appropriate

**Content Strategy:**
- Highlight 2-3 key insights from the report
- Make it relatable and actionable
- Show thought leadership
- Encourage discussion and engagement"""

        human_prompt = f"""User Profile:
Name: {user_profile['name']}
Job Title: {user_profile['job_title']}
Interests: {user_profile['interests']}

Report Content to Summarize:
{report_content[:3000]}

Create an engaging LinkedIn post that summarizes the key insights from this AI trends report.
Write as if {user_profile['name']}, a {user_profile['job_title']}, is sharing their perspective.
Make it personal, insightful, and engaging for a professional audience."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.standard_model.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn post from report: {str(e)}")
            raise

    @log_performance
    @retry_on_failure(max_retries=2)
    def generate_linkedin_post_from_topic(self, topic, user_profile):
        """
        Generate a LinkedIn post about a custom topic using web search.
        
        Searches the web for the latest information on a topic, then creates
        an engaging LinkedIn post based on the findings.
        
        Args:
            topic (str): The topic to write about
            user_profile (dict): User profile dictionary
            
        Returns:
            str: LinkedIn post text with formatting and hashtags
        """
        # Search web for information about the topic
        web_results = []
        if self.tavily_client:
            logger.info(f"Searching web for topic: {topic}")
            search_query = f"AI artificial intelligence {topic} latest news trends"
            web_results = self.search_web(search_query, max_results=5)
        
        # Prepare web search context
        web_context = ""
        if web_results:
            web_context = "Recent Information Found:\n\n"
            for i, result in enumerate(web_results, 1):
                web_context += f"{i}. {result['title']}\n"
                web_context += f"   {result['content'][:200]}...\n"
                web_context += f"   Source: {result['url']}\n\n"
        
        system_prompt = """You are a professional LinkedIn content creator specializing in AI and technology.
Your job is to create engaging, informative LinkedIn posts that drive engagement.

**Post Requirements:**
- Length: Approximately 300 words (2-3 short paragraphs)
- Style: Semi-casual, professional yet approachable
- Use emojis strategically (🤖 💡 🚀 ✨ 📊 🎯) - 3-5 total
- Include 5-8 relevant hashtags at the end
- Start with a hook that grabs attention
- End with a call-to-action or engaging question
- Use line breaks for readability
- Write in first person when appropriate

**Content Strategy:**
- Use the web search results as your primary information source
- Highlight key insights and trends
- Make it relatable and actionable
- Show thought leadership
- Encourage discussion and engagement
- Cite sources naturally (mention article titles or sources without URLs)"""

        human_prompt = f"""User Profile:
Name: {user_profile['name']}
Job Title: {user_profile['job_title']}
Interests: {user_profile['interests']}

Topic: {topic}

{web_context}

Create an engaging LinkedIn post about "{topic}" based on the latest information above.
Write as if {user_profile['name']}, a {user_profile['job_title']}, is sharing their insights.
Make it personal, insightful, and engaging for a professional audience."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.standard_model.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn post from topic: {str(e)}")
            raise
    
    # ========================================================================
    # REPORT GENERATION
    # ========================================================================
    
    def generate_full_report(self, user_profile, scrape_fresh_data=True):
        """
        Generate a complete personalized AI trends report.
        
        This is the main report generation function that:
        1. Optionally runs the web scraper to fetch fresh data
        2. Loads scraped newsletter articles
        3. Searches the web for latest trends (if Tavily is configured)
        4. Processes everything through AI to create a personalized report
        
        Args:
            user_profile (dict): User profile dictionary
            scrape_fresh_data (bool): If True, run scraper to get fresh data first
        
        Returns:
            str: Markdown formatted report
        """
        print("\n" + "="*80)
        print("🤖 AI AGENT PIPELINE - GENERATING PERSONALIZED REPORT")
        print("="*80)
        print(f"User: {user_profile['name']} ({user_profile['job_title']})")
        print("="*80 + "\n")
        
        # Step 1: Run scraper if requested
        if scrape_fresh_data:
            scraping_results = self.run_scrapers()
        else:
            print("ℹ️ Skipping web scraping, using existing data\n")
        
        report_sections = []
        
        # Header
        report_sections.append(f"# AI Trends Report for {user_profile['name']}")
        report_sections.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
        report_sections.append(f"**Profile:** {user_profile['job_title']}")
        report_sections.append("\n---\n")
        
        # Process Newsletter Articles (from ws_tool.py / beehiiv_articles.json)
        print("📰 Processing Newsletter Articles...")
        
        # Try to load the scraped data
        # The filename might be beehiiv_articles.json if ws_tool.py kept that name
        newsletter_data = self.load_json_file('beehiiv_articles.json')
        
        if newsletter_data:
            newsletter_report = self.process_newsletter_articles(
                newsletter_data, 
                "AI Newsletter", 
                user_profile
            )
            if newsletter_report:
                report_sections.append("## 📰 Latest AI Newsletter Highlights\n")
                report_sections.append(newsletter_report)
                report_sections.append("\n---\n")
                print("✅ Newsletter articles processed\n")
        else:
            print("⚠️ Newsletter data not available")
            print("   Make sure ws_tool.py has run and generated beehiiv_articles.json\n")
            report_sections.append("## ⚠️ No Newsletter Data Available\n")
            report_sections.append("*Please ensure the web scraper has run successfully and SCRAPER_BASE_URL is configured in .env*\n")
            report_sections.append("\n---\n")
        
        # Add web search section for latest trends
        print("🔍 Searching for latest AI trends...")
        if self.tavily_client:
            try:
                # Generate search query based on user interests
                search_query = f"latest AI artificial intelligence trends {' '.join(user_profile['tags'][:3])}"
                web_results = self.search_web(search_query, max_results=5)
                
                if web_results:
                    report_sections.append("## 🔍 Latest AI Trends from Web\n")
                    for result in web_results:
                        report_sections.append(f"### {result['title']}\n")
                        report_sections.append(f"{result['content']}\n")
                        report_sections.append(f"[Read more]({result['url']})\n\n")
                    report_sections.append("\n---\n")
                    print("✅ Web trends added\n")
            except Exception as e:
                print(f"⚠️ Web search failed: {str(e)}\n")
        else:
            print("⚠️ Tavily API not configured, skipping web search\n")
        
        # Footer
        report_sections.append("\n---")
        report_sections.append("\n*Report generated by AI Agent Pipeline*")
        report_sections.append(f"\n*Personalized for {user_profile['name']} based on your interests in: {', '.join(user_profile['tags'][:5])}*")
        
        # Combine all sections
        full_report = "\n".join(report_sections)
        
        print("="*80)
        print("✅ REPORT GENERATION COMPLETE")
        print("="*80 + "\n")
        
        return full_report
    
    # ========================================================================
    # YOUTUBE VIDEO RECOMMENDATIONS
    # ========================================================================
    
    @log_performance
    @retry_on_failure(max_retries=2)
    def get_personalized_youtube_videos(self, user_profile, max_results=8):
        """
        Get personalized YouTube video recommendations based on user profile.
        
        Uses AI to generate optimal search keywords based on the user's interests,
        then searches YouTube API for relevant videos.
        
        Args:
            user_profile (dict): User profile dictionary
            max_results (int): Number of videos to return (default: 8)
            
        Returns:
            dict: {
                'success': bool,
                'videos': list of video dicts,
                'keywords': str (search keywords used),
                'error': str (if success=False)
            }
        """
        if not Config.YOUTUBE_API_KEY:
            logger.error("YOUTUBE_API_KEY not set")
            return {
                'success': False,
                'error': 'YouTube API key not configured'
            }
        
        try:
            logger.info(f"Generating YouTube search keywords for {user_profile['name']}")
            
            # Step 1: Use AI to generate optimal search keywords
            keywords_prompt = f"""Based on this user profile, generate 3-5 specific search keywords for finding relevant AI/tech YouTube videos.

User Profile:
- Name: {user_profile['name']}
- Job Title: {user_profile['job_title']}
- Interests: {user_profile['interests']}
- Tags: {', '.join(user_profile['tags'])}

Return ONLY the search keywords as a comma-separated list, nothing else.
Example: "machine learning tutorials, AI news 2024, deep learning applications"
"""
            
            messages = [HumanMessage(content=keywords_prompt)]
            response = self.standard_model.invoke(messages)
            search_keywords = response.content.strip()
            
            logger.info(f"Generated keywords: {search_keywords}")
            
            # Step 2: Search YouTube with generated keywords
            youtube_api_url = "https://www.googleapis.com/youtube/v3/search"
            
            params = {
                'part': 'snippet',
                'q': search_keywords,
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',
                'relevanceLanguage': 'en',
                'videoDuration': 'medium',  # 4-20 minutes
                'key': Config.YOUTUBE_API_KEY
            }
            
            logger.info(f"Calling YouTube API with keywords: {search_keywords}")
            youtube_response = requests.get(youtube_api_url, params=params, timeout=10)
            youtube_response.raise_for_status()
            
            data = youtube_response.json()
            
            # Step 3: Format the results
            videos = []
            for item in data.get('items', []):
                video = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:200] + '...' if len(item['snippet']['description']) > 200 else item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                }
                videos.append(video)
            
            logger.info(f"Successfully fetched {len(videos)} YouTube videos")
            
            return {
                'success': True,
                'videos': videos,
                'keywords': search_keywords
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API error: {str(e)}")
            return {
                'success': False,
                'error': f'YouTube API request failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error getting YouTube videos: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }