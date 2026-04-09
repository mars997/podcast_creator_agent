"""
Step 39: Source Selection Agent

Intelligent agent that automatically finds and selects relevant sources for topics.
Searches web, filters quality, ranks relevance, and curates source list.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json

from providers.factory import create_llm_provider, ProviderConfig, detect_available_providers
import config


class SourceSelectionAgent:
    """Intelligently selects sources for podcast topics"""

    def __init__(self, llm_provider):
        self.llm_provider = llm_provider

    def suggest_search_queries(self, topic: str, num_queries: int = 3) -> List[str]:
        """Generate effective search queries for a topic"""

        prompt = f"""Generate {num_queries} effective search queries to find high-quality sources about: {topic}

Requirements:
- Queries should find authoritative, recent information
- Include variety (news, analysis, research, explanations)
- Be specific enough to filter noise
- Format: one query per line

Generate the search queries:"""

        response = self.llm_provider.generate_text(prompt)

        # Parse queries from response
        queries = [line.strip() for line in response.split('\n') if line.strip() and not line.strip().startswith('#')]

        return queries[:num_queries]

    def evaluate_source_quality(self, source_text: str, source_url: str) -> Dict:
        """Evaluate quality and relevance of a source"""

        prompt = f"""Evaluate this source for podcast creation:

URL: {source_url}

Content preview:
{source_text[:2000]}...

Rate the source on:
1. RELEVANCE (1-10): How relevant is this to creating podcast content?
2. QUALITY (1-10): How authoritative and well-written is it?
3. FRESHNESS (1-10): How recent/current is the information?
4. USABILITY (1-10): How easy to extract key points?

Provide scores in this format:
RELEVANCE: X
QUALITY: X
FRESHNESS: X
USABILITY: X
OVERALL: X
REASON: Brief explanation

Evaluate the source:"""

        response = self.llm_provider.generate_text(prompt)

        # Parse scores
        scores = {
            "relevance": 5,
            "quality": 5,
            "freshness": 5,
            "usability": 5,
            "overall": 5,
            "reason": "Evaluation unavailable"
        }

        for line in response.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if key in scores:
                    if key == "reason":
                        scores[key] = value
                    else:
                        try:
                            scores[key] = int(value)
                        except ValueError:
                            pass

        return scores

    def rank_sources(self, sources: List[Dict]) -> List[Dict]:
        """Rank sources by overall quality score"""

        return sorted(sources, key=lambda s: s.get("scores", {}).get("overall", 0), reverse=True)

    def select_best_sources(self, topic: str, sources: List[Dict], max_sources: int = 5) -> List[Dict]:
        """Select best sources for topic"""

        prompt = f"""From these sources about "{topic}", select the best {max_sources} for creating a podcast episode.

Sources:
"""
        for i, source in enumerate(sources, 1):
            prompt += f"\n{i}. {source.get('url', 'Unknown')}"
            prompt += f"\n   Quality: {source.get('scores', {}).get('overall', 'N/A')}/10"
            prompt += f"\n   Preview: {source.get('text', '')[:200]}..."

        prompt += f"""

Select the top {max_sources} sources that provide:
- Complementary perspectives
- Mix of depth and breadth
- Good coverage of the topic
- High quality and reliability

List the source numbers (comma-separated):"""

        response = self.llm_provider.generate_text(prompt)

        # Parse selection
        try:
            selected_indices = [int(x.strip())-1 for x in response.split(',') if x.strip().isdigit()]
            selected = [sources[i] for i in selected_indices if 0 <= i < len(sources)]
            return selected[:max_sources]
        except:
            # Fallback: just return top ranked
            return sources[:max_sources]

    def generate_source_summary(self, sources: List[Dict]) -> str:
        """Generate summary of selected sources"""

        summary = "Selected Sources:\n\n"

        for i, source in enumerate(sources, 1):
            summary += f"{i}. {source.get('url', 'Unknown')}\n"
            scores = source.get('scores', {})
            summary += f"   Overall: {scores.get('overall', 'N/A')}/10\n"
            summary += f"   Reason: {scores.get('reason', 'No evaluation')}\n\n"

        return summary


def simulate_source_search(topic: str, num_sources: int = 10) -> List[Dict]:
    """Simulate finding sources (placeholder for real web search)"""

    # In real implementation, this would use web search API
    # For now, return simulated sources

    simulated_sources = [
        {
            "url": f"https://example.com/article-{i}",
            "title": f"Article about {topic} - Part {i}",
            "text": f"This is simulated content about {topic}. Contains relevant information and analysis.",
            "date": datetime.now().isoformat()
        }
        for i in range(1, num_sources + 1)
    ]

    return simulated_sources


def main():
    """Source selection agent demo"""
    print("\n" + "="*70)
    print("Step 39: Source Selection Agent")
    print("="*70)

    # Check providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available")
        return

    # Setup
    provider_name = list(available.keys())[0]
    provider_config = ProviderConfig(llm_provider=provider_name)
    llm_provider = create_llm_provider(provider_config)

    print(f"\n[OK] Agent initialized with {provider_name}")

    agent = SourceSelectionAgent(llm_provider)

    # Get topic
    topic = input("\nEnter podcast topic: ").strip()
    if not topic:
        topic = "The Future of Renewable Energy"
        print(f"[INFO] Using demo topic: {topic}")

    # Step 1: Generate search queries
    print("\n[1/4] Generating search queries...")
    queries = agent.suggest_search_queries(topic, num_queries=3)

    print(f"\n[OK] Generated queries:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")

    # Step 2: Simulate finding sources
    print("\n[2/4] Finding sources...")
    print("[INFO] (Simulated search - real implementation would use web search API)")

    raw_sources = simulate_source_search(topic, num_sources=8)
    print(f"[OK] Found {len(raw_sources)} potential sources")

    # Step 3: Evaluate sources
    print("\n[3/4] Evaluating source quality...")

    for source in raw_sources:
        print(f"[INFO] Evaluating: {source['url']}")
        scores = agent.evaluate_source_quality(source['text'], source['url'])
        source['scores'] = scores

    print(f"[OK] All sources evaluated")

    # Rank sources
    ranked_sources = agent.rank_sources(raw_sources)

    print(f"\n[OK] Sources ranked:")
    for i, source in enumerate(ranked_sources[:5], 1):
        print(f"  {i}. {source['url']} - Overall: {source['scores']['overall']}/10")

    # Step 4: Select best sources
    print("\n[4/4] Selecting best sources...")

    max_sources = 5
    selected_sources = agent.select_best_sources(topic, ranked_sources, max_sources)

    print(f"\n[OK] Selected {len(selected_sources)} sources")

    # Generate summary
    summary = agent.generate_source_summary(selected_sources)

    print(f"\n{'='*70}")
    print("Source Selection Complete")
    print(f"{'='*70}")
    print(summary)

    # Save selection results
    output_dir = Path(config.OUTPUT_ROOT) / "source_selections"
    output_dir.mkdir(exist_ok=True)

    selection_file = output_dir / f"selection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    selection_data = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "search_queries": queries,
        "total_sources_found": len(raw_sources),
        "sources_selected": len(selected_sources),
        "selected_sources": selected_sources
    }

    with open(selection_file, 'w', encoding='utf-8') as f:
        json.dump(selection_data, f, indent=2)

    print(f"\n[OK] Selection saved: {selection_file}")

    # Offer to create episode
    create_episode = input("\nCreate episode with these sources? (y/n): ").strip().lower()

    if create_episode == 'y':
        from step37_automated_generation import generate_automated_episode, AUTOMATION_PROFILES

        # Extract source texts
        source_texts = [s['text'] for s in selected_sources]

        print("\n[INFO] Generating episode with selected sources...")

        result = generate_automated_episode(
            topic=topic,
            profile=AUTOMATION_PROFILES["trending_topics"],
            sources=source_texts
        )

        if result["success"]:
            print(f"\n[OK] Episode created: {result['episode_id']}")


if __name__ == "__main__":
    main()
