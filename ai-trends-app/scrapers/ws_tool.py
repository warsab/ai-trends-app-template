import requests
from bs4 import BeautifulSoup
import time
import json
import re
import os
from typing import List, Dict, Optional
from urllib.parse import urljoin
from datetime import datetime

# -*- coding: utf-8 -*-
import sys
import io

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================================
# CONFIGURATION
# ============================================================================
# 
# This scraper is designed to scrape Beehiiv newsletter homepages or similar
# blog/newsletter sites that list articles with links.
#
# TO CUSTOMIZE FOR YOUR USE:
# 1. Set the SCRAPER_BASE_URL environment variable in your .env file, OR
# 2. Change the default URL below to your target newsletter/blog URL
# 
# Example URLs you might use:
# - https://aiengineering.beehiiv.com/
# - https://yournewsletter.beehiiv.com/
# - https://yourblog.com/
# ============================================================================

# Get URL from environment variable or use default
BASE_URL = os.getenv('SCRAPER_BASE_URL', 'https://example.beehiiv.com/')

# Print warning if using default URL
if BASE_URL == 'https://example.beehiiv.com/':
    print("⚠ WARNING: Using default example URL. Please set SCRAPER_BASE_URL in your .env file!")
    print("   Example: SCRAPER_BASE_URL=https://yournewsletter.beehiiv.com/")

# Determine the correct base directory (works for local dev and deployment)
def get_base_dir():
    """Get the base directory for the application"""
    current_dir = os.getcwd()
    
    # Check if we're in ai-trends-app directory
    if os.path.basename(current_dir) == "ai-trends-app":
        return "."
    
    # Check if ai-trends-app exists as subdirectory
    if os.path.exists("ai-trends-app"):
        return "ai-trends-app"
    
    # Check if we're inside scrapers folder
    if os.path.basename(current_dir) == "scrapers":
        return ".."
    
    # Default to current directory
    return "."

BASE_DIR = get_base_dir()

# Create data directories if they don't exist
DATA_DIR = os.path.join(BASE_DIR, "data", "scraped")
BACKUP_DIR = os.path.join(BASE_DIR, "data", "backups")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Storage for scraped data
scraped_articles = []


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_title_from_slug(slug: str) -> str:
    """Convert URL slug to readable title."""
    slug = slug.replace('p/', '')
    title = slug.replace('-', ' ').title()
    return title


def find_subheading_near_link(link_element, soup) -> Optional[str]:
    """
    Try to find subheading text near a link by searching in multiple ways.
    """
    # Method 1: Look in immediate parent's siblings
    parent = link_element.parent
    if parent:
        for sibling in parent.find_next_siblings():
            text = clean_text(sibling.get_text())
            if text and ('..' in text or 'PLUS:' in text.upper()) and len(text) > 15:
                return text
            # Break after checking a few siblings
            if sibling.name in ['div', 'article'] and len(list(parent.find_next_siblings())) > 3:
                break
    
    # Method 2: Look in grandparent's descendants
    grandparent = parent.parent if parent else None
    if grandparent:
        # Look for text that looks like a description
        for elem in grandparent.find_all(['p', 'div', 'span']):
            text = clean_text(elem.get_text())
            if text and ('..' in text or 'PLUS:' in text.upper()) and len(text) > 15:
                # Make sure it's not the title
                link_text = clean_text(link_element.get_text())
                if text != link_text:
                    return text
    
    # Method 3: Search the entire nearby area for ".. PLUS:" patterns
    # Get a larger container
    container = link_element.find_parent(['article', 'section'])
    if not container:
        # Go up a few levels
        container = link_element.parent
        for _ in range(3):
            if container and container.parent:
                container = container.parent
            else:
                break
    
    if container:
        # Find all text elements
        all_text = container.find_all(string=re.compile(r'\.\.|PLUS:', re.I))
        for text_elem in all_text:
            text = clean_text(text_elem)
            if len(text) > 15:
                return text
    
    return None


def scrape_beehiiv_homepage(url: str = BASE_URL) -> List[Dict]:
    """
    Scrape a Beehiiv newsletter homepage (or similar site) for article listings.
    
    NOTE: This scraper is optimized for Beehiiv-style layouts but may work with
    other blog/newsletter platforms. You may need to adjust the selectors if
    your target site has a different structure.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        seen_urls = set()
        
        # Find all links that point to posts (/p/ pattern)
        post_links = soup.find_all('a', href=re.compile(r'/p/[^/]+$'))
        
        print(f"Found {len(post_links)} post links")
        
        # Also extract all subheading-like text from the page for matching
        all_subheadings = {}
        for text_elem in soup.find_all(string=re.compile(r'\.\.|PLUS:', re.I)):
            text = clean_text(text_elem)
            if len(text) > 15 and len(text) < 200:
                # Try to find associated link nearby
                parent = text_elem.parent
                nearby_link = None
                
                # Search up and around for a link
                for _ in range(5):
                    if parent:
                        nearby_link = parent.find('a', href=re.compile(r'/p/'))
                        if nearby_link:
                            break
                        parent = parent.parent
                
                if nearby_link:
                    href = nearby_link.get('href', '')
                    all_subheadings[href] = text
        
        for link in post_links:
            try:
                article_data = {
                    'title': None,
                    'subheading': None,
                    'article_url': None,
                    'date': None,
                    'author': None
                }
                
                # Get URL
                href = link.get('href', '')
                article_data['article_url'] = urljoin(url, href)
                
                # Skip duplicates
                if article_data['article_url'] in seen_urls:
                    continue
                seen_urls.add(article_data['article_url'])
                
                # Extract slug
                url_slug = href.split('/p/')[-1].rstrip('/')
                
                # Get title from link text
                link_text = clean_text(link.get_text())
                if link_text and len(link_text) > 5:
                    article_data['title'] = link_text
                else:
                    article_data['title'] = extract_title_from_slug(url_slug)
                
                # Try to find subheading
                # First check our pre-extracted subheadings
                if href in all_subheadings:
                    article_data['subheading'] = all_subheadings[href]
                else:
                    # Try to find it near the link
                    article_data['subheading'] = find_subheading_near_link(link, soup)
                
                # Try to find date and author
                container = link.find_parent(['article', 'div', 'section'])
                
                if container:
                    # Look for date patterns
                    for elem in container.find_all(['span', 'div', 'p', 'time']):
                        text = clean_text(elem.get_text())
                        # Match patterns like "4 hours ago", "Sep 29, 2025"
                        if re.search(r'\d+\s+(hour|day|week|month)s?\s+ago|[A-Z][a-z]{2}\s+\d+,\s+\d{4}', text, re.I):
                            article_data['date'] = text
                            break
                    
                    # Look for author - CUSTOMIZE THIS for your site
                    # Remove or modify the author pattern below to match your site
                    author_elem = container.find(string=re.compile(r'by\s+\w+', re.I))
                    if author_elem:
                        article_data['author'] = clean_text(author_elem)
                
                articles.append(article_data)
            
            except Exception as e:
                print(f"  ⚠ Error processing link: {e}")
                continue
        
        print(f"\n✓ Successfully scraped {len(articles)} articles from homepage")
        
        # Summary of what was found
        with_subheadings = sum(1 for a in articles if a['subheading'])
        print(f"  - Articles with subheadings: {with_subheadings}/{len(articles)}")
        
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching {url}: {e}")
        return []
    except Exception as e:
        print(f"✗ Error parsing {url}: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_to_json(data: List[Dict], filename: str = None):
    """
    Save scraped data to JSON file in the data directory.
    
    Args:
        data: List of article dictionaries to save
        filename: Optional custom filename (without path)
    """
    if filename is None:
        # Use fixed filename for consistency
        filename = 'beehiiv_articles.json'
    
    # Ensure filename doesn't have a path
    filename = os.path.basename(filename)
    
    # Create full path in data directory
    filepath = os.path.join(DATA_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Data saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"✗ Error saving file: {e}")
        return None


# Main execution
if __name__ == "__main__":
    print("=" * 70)
    print("Newsletter/Blog Homepage Scraper")
    print("=" * 70)
    print(f"Target URL: {BASE_URL}")
    print(f"Output directory: {os.path.abspath(DATA_DIR)}")
    print()
    
    # Scrape the homepage
    scraped_articles = scrape_beehiiv_homepage(BASE_URL)
    
    # Automatically save to JSON in data folder
    if scraped_articles:
        saved_path = save_to_json(scraped_articles)
        if saved_path:
            print(f"\n✓ Total articles scraped: {len(scraped_articles)}")
            print(f"✓ File saved at: {os.path.abspath(saved_path)}")
            
            # Also create a timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f'beehiiv_articles_backup_{timestamp}.json'
            backup_filepath = os.path.join(BACKUP_DIR, backup_filename)
            
            try:
                with open(backup_filepath, 'w', encoding='utf-8') as f:
                    json.dump(scraped_articles, f, indent=2, ensure_ascii=False)
                print(f"✓ Backup saved at: {os.path.abspath(backup_filepath)}")
            except Exception as e:
                print(f"⚠ Error saving backup: {e}")
    else:
        print("\n⚠ No articles found.")