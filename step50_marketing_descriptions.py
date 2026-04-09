"""Step 50: Generate Podcast-Ready Descriptions"""
from providers.factory import ProviderConfig, create_llm_provider, detect_available_providers

def generate_marketing_content(topic, script):
    available = detect_available_providers()
    if not available:
        return None
    
    provider = list(available.keys())[0]
    config = ProviderConfig(llm_provider=provider, tts_provider=provider)
    llm = create_llm_provider(config)
    
    prompt = f"""Generate marketing content for this podcast:

Topic: {topic}

Script excerpt: {script[:500]}...

Generate:
1. SEO-friendly title (60 chars max)
2. Episode description (150 chars)
3. Full description (300 words)
4. Social media post (280 chars)
5. Keywords (10 keywords)
"""
    
    return llm.generate_text(prompt)

if __name__ == '__main__':
    print('Step 50: Marketing Descriptions')
    print('[OK] Marketing generator ready')
