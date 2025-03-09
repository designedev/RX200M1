import requests
from bs4 import BeautifulSoup
from conf.logging_config import logger

async def extract_media_links(url: str) -> dict:
    """Extract image and video links from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the div with class 'view_content'
        view_content_div = soup.find('div', class_='view_content')
        
        if not view_content_div:
            logger.error(f"No 'view_content' div found in URL {url}")
            return None
        
        # Extract image links within the 'view_content' div
        images = [img['src'] for img in view_content_div.find_all('img') if 'src' in img.attrs]
        
        # Extract video links within the 'view_content' div
        videos = [video['src'] for video in view_content_div.find_all('video') if 'src' in video.attrs]
        youtube_links = [a['href'] for a in view_content_div.find_all('a') if 'href' in a.attrs and 'youtube.com' in a['href']]
        iframe_youtube_links = [iframe['src'] for iframe in view_content_div.find_all('iframe') if 'src' in iframe.attrs and 'youtube.com' in iframe['src']] 
        videos.extend(youtube_links)
        videos.extend(iframe_youtube_links)
        media_links = {
            'images': images,
            'videos': videos
        }
        
        logger.info(f"Extracted media links from {url}: {media_links}")
        return media_links
    except Exception as e:
        logger.error(f"Failed to extract media links from URL {url}: {e}")
        return None