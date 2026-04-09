"""Step 51: RSS Publishing Support"""
from datetime import datetime

def generate_rss_item(episode_metadata, audio_url):
    item = f"""
    <item>
        <title>{episode_metadata.get('topic', 'Untitled')}</title>
        <description>{episode_metadata.get('description', '')}</description>
        <pubDate>{episode_metadata.get('created_at', '')}</pubDate>
        <enclosure url="{audio_url}" type="audio/mpeg"/>
        <guid>{episode_metadata.get('episode_id', '')}</guid>
    </item>
    """
    return item

if __name__ == '__main__':
    print('Step 51: RSS Feed Generator')
    print('[OK] RSS function ready')
