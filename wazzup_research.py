import requests
from web_scraper import get_website_text_content

def research_wazzup_api():
    """Research Wazzup24.ru API documentation"""
    url = "https://wazzup24.ru/help/api-ru/shemy-integracij/"
    
    try:
        # Get the website content
        content = get_website_text_content(url)
        
        if content:
            print("Wazzup24.ru API Integration Documentation:")
            print("=" * 60)
            print(content)
            return content
        else:
            print("Could not extract content from the website")
            return None
            
    except Exception as e:
        print(f"Error accessing Wazzup24.ru documentation: {e}")
        return None

if __name__ == "__main__":
    research_wazzup_api()