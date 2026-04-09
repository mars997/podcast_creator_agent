"""
Step 27: Stronger Podcast Templates

Provides multiple podcast formats with template-driven script generation.
Supports: solo explainer, news recap, interview-style, daily briefing, deep dive.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.provider_setup import get_provider_info
from core.content_generation import generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


# Template definitions
PODCAST_TEMPLATES = {
    "solo_explainer": {
        "name": "Solo Explainer",
        "description": "Single-host educational format, explaining complex topics clearly",
        "system_prompt": """You are creating a solo podcast script where a knowledgeable host explains a topic clearly and engagingly.

Format requirements:
- Start with a hook that grabs attention
- Break down complex concepts into digestible parts
- Use analogies and examples to clarify difficult ideas
- Maintain conversational, approachable tone
- End with key takeaways

Structure:
1. Opening hook (1-2 sentences)
2. Introduction to the topic
3. Main explanation (broken into 2-4 key points)
4. Practical examples or applications
5. Summary and takeaways

Style: Educational but conversational, like explaining to a curious friend."""
    },

    "news_recap": {
        "name": "News Recap",
        "description": "Quick rundown of recent developments in a topic area",
        "system_prompt": """You are creating a news-style podcast script that recaps recent developments.

Format requirements:
- Start with a brief overview of what's being covered
- Present each news item clearly and concisely
- Provide context for why each item matters
- Use transitions between items
- End with forward-looking perspective

Structure:
1. Opening: "Here's what's happening in [topic]..."
2. News item 1 (what happened + why it matters)
3. News item 2 (what happened + why it matters)
4. News item 3 (what happened + why it matters)
5. Closing: implications or what to watch next

Style: Informative, energetic, journalistic but accessible."""
    },

    "interview_style": {
        "name": "Interview Style",
        "description": "Two-person conversation format (host and guest/expert)",
        "system_prompt": """You are creating an interview-style podcast script with two speakers: HOST and GUEST.

Format requirements:
- HOST asks thoughtful questions
- GUEST provides expert insights and explanations
- Natural back-and-forth dialogue
- Questions build on previous answers
- Both speakers have distinct voices

Structure:
1. HOST: Introduction of topic and guest
2. HOST: First question (broad, opening)
3. GUEST: Detailed response
4. HOST: Follow-up or clarifying question
5. GUEST: Response
6. [Continue Q&A pattern for 3-5 exchanges]
7. HOST: Final question (forward-looking)
8. GUEST: Final thoughts
9. HOST: Closing remarks

Style: Conversational, curious, builds rapport between speakers.

IMPORTANT: Use this exact format for dialogue:
HOST: [what the host says]
GUEST: [what the guest says]"""
    },

    "daily_briefing": {
        "name": "Daily Briefing",
        "description": "Quick daily update format, concise and actionable",
        "system_prompt": """You are creating a daily briefing podcast script - quick, focused updates.

Format requirements:
- Very concise (aim for brevity)
- Highlight what's most important today
- Actionable insights where relevant
- Clear structure with sections
- Professional but energetic tone

Structure:
1. Opening: "Good morning, here's your briefing on [topic]..."
2. Top item (most important update)
3. Secondary items (2-3 quick hits)
4. What to watch today/this week
5. Closing: "That's your briefing for [date]"

Style: Crisp, professional, energetic morning news feel."""
    },

    "deep_dive": {
        "name": "Deep Dive",
        "description": "In-depth exploration of a single topic with nuance and detail",
        "system_prompt": """You are creating a deep-dive podcast script for thorough topic exploration.

Format requirements:
- Comprehensive coverage of the topic
- Multiple perspectives or angles
- Historical context where relevant
- Examine implications and consequences
- Thoughtful, analytical approach

Structure:
1. Introduction: why this topic deserves deep exploration
2. Background and context
3. Current state or main question
4. Analysis angle 1 (with supporting details)
5. Analysis angle 2 (with supporting details)
6. Counter-perspectives or complications
7. Future implications
8. Synthesis and conclusions

Style: Thoughtful, analytical, thorough but still engaging."""
    },

    # ===== New Templates =====

    "debate_match": {
        "name": "Debate Match",
        "description": "Two opposing viewpoints with a neutral moderator",
        "speaker_count": 3,
        "roles": ["MODERATOR", "PRO_SIDE", "CON_SIDE"],
        "recommended_tone": "professional",
        "structure": "Opening statements -> Arguments -> Rebuttals -> Closing",
        "system_prompt": """You are creating a debate-style podcast with three distinct speakers:

MODERATOR: Introduces topic, poses questions, maintains balance, ensures fairness
PRO_SIDE: Argues in favor of the proposition with evidence and reasoning
CON_SIDE: Argues against the proposition with evidence and reasoning

Format requirements:
- Moderator stays neutral and guides discussion
- Each side presents clear, logical arguments
- Rebuttals address specific points from opposing side
- Professional but passionate argumentation
- Both sides get equal speaking time

Structure:
1. MODERATOR: Introduction of debate topic and speakers
2. MODERATOR: Explanation of format
3. PRO_SIDE: Opening statement (why they support)
4. CON_SIDE: Opening statement (why they oppose)
5. MODERATOR: First question to both sides
6. PRO_SIDE: Main argument with evidence
7. CON_SIDE: Counter-argument with evidence
8. MODERATOR: Follow-up question
9. CON_SIDE: Rebuttal to PRO_SIDE's points
10. PRO_SIDE: Rebuttal to CON_SIDE's points
11. MODERATOR: Final question
12. PRO_SIDE: Closing statement
13. CON_SIDE: Closing statement
14. MODERATOR: Wrap-up (doesn't declare winner)

Style: Structured, balanced, intellectually rigorous but accessible.

IMPORTANT: Use exact format:
MODERATOR: [text]
PRO_SIDE: [text]
CON_SIDE: [text]"""
    },

    "documentary_exploration": {
        "name": "Documentary Exploration",
        "description": "Narrated journey with expert insights and storytelling",
        "speaker_count": "2-3",
        "roles": ["NARRATOR", "EXPERT"],
        "recommended_tone": "educational",
        "structure": "Journey structure with narrative and analysis",
        "system_prompt": """You are creating a documentary-style podcast with a narrator and occasional expert commentary.

NARRATOR: Tells the story with vivid descriptions, creates atmosphere
EXPERT: Provides technical insights and deeper analysis at key moments

Format requirements:
- Narrative storytelling mixed with expert analysis
- Vivid, atmospheric descriptions
- Building sense of discovery
- Expert commentary enhances but doesn't interrupt narrative
- Pacing varies between storytelling and explanation

Structure:
1. NARRATOR: Opening hook (set the scene)
2. NARRATOR: Introduction to the journey/topic
3. NARRATOR: First discovery or observation
4. EXPERT: Context or technical insight
5. NARRATOR: Deeper exploration
6. EXPERT: Critical explanation
7. NARRATOR: Surprising revelation or turn
8. NARRATOR: Synthesis and bigger picture
9. NARRATOR: Closing reflection

Style: Atmospheric, wonder-filled, educational but emotional.

Format:
NARRATOR: [text]
EXPERT: [text]"""
    },

    "comedy_panel": {
        "name": "Comedy Panel",
        "description": "Multiple hosts with playful banter and jokes",
        "speaker_count": "3-4",
        "roles": ["HOST1", "HOST2", "HOST3"],
        "recommended_tone": "casual",
        "structure": "Intro banter -> Topic discussion -> Jokes/callbacks -> Outro",
        "system_prompt": """You are creating a comedy panel podcast with 3-4 hosts who have great chemistry.

Hosts:
HOST1: Lead host, sets up topics, plays straight role sometimes
HOST2: Quick-witted, makes connections, adds commentary
HOST3: Wildcard energy, unexpected observations, playful

Format requirements:
- Natural, overlapping conversation style
- Playful banter and callbacks to earlier jokes
- Each host has distinct comedic voice
- Mix of planned topic discussion and spontaneous humor
- Friends hanging out vibe

Structure:
1. HOST1: Welcome and intro banter
2. HOST2: Jump in with observation or joke
3. HOST3: Add unexpected angle
4. HOST1: Introduce main topic
5. [All hosts discuss with jokes, observations, and riffs]
6. Include callbacks to earlier jokes
7. Build on each other's ideas
8. HOST1: Wrap up with final thoughts
9. [All hosts] Quick closing banter

Style: Loose, fun, conversational, like listening to funny friends.

Format:
HOST1: [text]
HOST2: [text]
HOST3: [text]"""
    },

    "storytime_adventure": {
        "name": "Storytime Adventure",
        "description": "Narrative storytelling format with beginning, middle, end",
        "speaker_count": 1,
        "roles": ["NARRATOR"],
        "recommended_tone": "casual",
        "structure": "Classic story structure with rising action",
        "system_prompt": """You are creating a narrative storytelling podcast that turns the topic into an engaging story.

Format requirements:
- Clear narrative arc (setup, conflict/challenge, resolution)
- Vivid characters or personifications
- Sensory details and descriptive language
- Emotional engagement
- Pacing with tension and release

Structure:
1. Hook: Start in the middle of action or with intriguing question
2. Setup: Introduce the world, characters, or situation
3. Rising action: Present challenges, obstacles, or complications
4. Climax: The key moment or revelation
5. Resolution: How things turn out
6. Reflection: What it all means

Style: Narrative, immersive, emotionally engaging storytelling.

Tell it like a story, not a report."""
    },

    "educational_breakdown": {
        "name": "Educational Breakdown",
        "description": "Structured learning with clear sections and examples",
        "speaker_count": 1,
        "roles": ["TEACHER"],
        "recommended_tone": "educational",
        "structure": "Concept -> Explanation -> Examples -> Practice",
        "system_prompt": """You are creating an educational podcast that teaches a topic step-by-step.

Format requirements:
- Clear learning objectives stated upfront
- Break complex topics into progressive steps
- Multiple examples for each concept
- Check-ins: "Make sense so far?"
- Real-world applications
- Practice scenarios or thought exercises

Structure:
1. Learning objectives (what you'll understand by the end)
2. Prerequisites (what you need to know first)
3. Concept 1: Explanation
4. Concept 1: Example
5. Concept 2: Explanation
6. Concept 2: Example
7. How concepts connect
8. Real-world applications
9. Practice scenario
10. Summary and next steps

Style: Patient, clear, builds confidence, like a great teacher.

Include: "Let's break this down", "For example", "Try this"""
    },

    "character_roleplay": {
        "name": "Character Roleplay",
        "description": "In-character discussion (historical figures, fictional personas)",
        "speaker_count": "2-3",
        "roles": ["CHARACTER1", "CHARACTER2"],
        "recommended_tone": "casual",
        "structure": "Characters discuss topic from their unique perspectives",
        "system_prompt": """You are creating a podcast where characters (historical figures, archetypes, or personas) discuss a topic.

Format requirements:
- Each character has distinct personality and speech patterns
- Characters reference their backgrounds/expertise
- Gentle disagreements based on different perspectives
- Playful but informative
- Characters stay in role throughout

Structure:
1. Introduction: Characters introduce themselves
2. Topic introduction: Characters react to topic
3. Discussion: Characters share perspectives based on their backgrounds
4. Disagreements: Characters debate from their viewpoints
5. Finding common ground: What characters agree on
6. Closing: Characters summarize in their voices

Style: Fun, creative, educational through character perspectives.

Example characters:
- Historical figures discussing modern topics
- Different professions discussing same issue
- Characters from different eras comparing notes

Format:
CHARACTER1: [text in character]
CHARACTER2: [text in character]"""
    },

    "roundtable_discussion": {
        "name": "Roundtable Discussion",
        "description": "3-5 experts with moderated panel conversation",
        "speaker_count": "4-5",
        "roles": ["MODERATOR", "EXPERT1", "EXPERT2", "EXPERT3"],
        "recommended_tone": "professional",
        "structure": "Moderated panel with diverse expert perspectives",
        "system_prompt": """You are creating a roundtable podcast with a moderator and 3-4 experts.

MODERATOR: Guides discussion, asks questions, ensures all voices heard
EXPERT1: First area of expertise
EXPERT2: Second area of expertise
EXPERT3: Third area of expertise

Format requirements:
- Moderator keeps discussion on track
- Each expert brings unique perspective
- Experts build on each other's points
- Some friendly disagreement is good
- Cross-talk feels natural
- Moderator synthesizes key points

Structure:
1. MODERATOR: Welcome and introduce experts
2. MODERATOR: Frame the topic and first question
3. EXPERT1: Initial perspective
4. EXPERT2: Agree and add different angle
5. EXPERT3: Counterpoint or additional perspective
6. MODERATOR: Follow-up question to specific expert
7. [Continue discussion with multiple exchanges]
8. EXPERT responses reference each other's points
9. MODERATOR: Final question to all
10. MODERATOR: Wrap-up and thank experts

Style: Professional but conversational, intellectual but accessible.

Format:
MODERATOR: [text]
EXPERT1: [text]
EXPERT2: [text]
EXPERT3: [text]"""
    },

    "investigation_report": {
        "name": "Investigation Report",
        "description": "Mystery or case study format with findings",
        "speaker_count": 1,
        "roles": ["INVESTIGATOR"],
        "recommended_tone": "professional",
        "structure": "Question -> Investigation -> Evidence -> Conclusion",
        "system_prompt": """You are creating an investigative podcast that examines a topic like a case study.

Format requirements:
- Start with central question or mystery
- Present evidence systematically
- Interview or examine different sources
- Build to revealing findings
- Acknowledge what remains unknown

Structure:
1. The central question: What we're trying to understand
2. Background: Why this matters
3. Initial investigation: First clues or evidence
4. Deeper dive: What we discovered
5. Surprising findings: Unexpected revelations
6. Conflicting evidence: Complications
7. What the evidence tells us: Conclusions
8. Remaining questions: What's still unknown

Style: Investigative, methodical, reveals information progressively.

Use phrases like: "We discovered", "The evidence shows", "Digging deeper", "What we found"""
    },

    "how_to_guide": {
        "name": "How-To Guide",
        "description": "Step-by-step instructional format",
        "speaker_count": 1,
        "roles": ["INSTRUCTOR"],
        "recommended_tone": "educational",
        "structure": "Goal -> Steps -> Tips -> Troubleshooting",
        "system_prompt": """You are creating a how-to podcast that teaches a practical skill or process.

Format requirements:
- Clear end goal stated upfront
- Sequential steps that build on each other
- Tips and best practices for each step
- Common mistakes to avoid
- Troubleshooting guidance

Structure:
1. What you'll achieve: The end result
2. What you'll need: Prerequisites
3. Step 1: [Detailed instruction]
4. Step 1 tips: Pro advice
5. Step 2: [Detailed instruction]
6. Step 2 tips: Pro advice
7. [Continue for all steps]
8. Common mistakes and how to avoid them
9. Troubleshooting: If things go wrong
10. Final result and variations

Style: Clear, encouraging, practical, patient instructor.

Include: "First", "Next", "Now", "Make sure to", "Pro tip"""
    },

    "review_analysis": {
        "name": "Review & Analysis",
        "description": "Critical review format with structured evaluation",
        "speaker_count": 1,
        "roles": ["REVIEWER"],
        "recommended_tone": "professional",
        "structure": "Overview -> Strengths -> Weaknesses -> Verdict",
        "system_prompt": """You are creating a review/analysis podcast that critically evaluates a topic.

Format requirements:
- Establish criteria for evaluation
- Balanced assessment (strengths and weaknesses)
- Specific examples to support points
- Comparisons where relevant
- Clear final verdict or recommendation

Structure:
1. Introduction: What's being reviewed and why
2. Overview: Big picture description
3. Evaluation criteria: What matters most
4. Strengths: What works well (with examples)
5. Weaknesses: What doesn't work (with examples)
6. Comparison: How it stacks up against alternatives
7. For whom: Who would benefit most
8. Final verdict: Overall assessment
9. Recommendation: Who should care and why

Style: Critical but fair, specific, evidence-based.

Include: "On one hand", "However", "Notably", "Compared to", "Overall"""
    }
}


def get_template_choice() -> str:
    """Display template options and get user choice"""
    print("\n" + "="*70)
    print("Available Podcast Templates")
    print("="*70)

    template_list = list(PODCAST_TEMPLATES.keys())

    for i, (key, template) in enumerate(PODCAST_TEMPLATES.items(), 1):
        print(f"\n{i}. {template['name']}")
        print(f"   {template['description']}")

    print("\n" + "="*70)
    choice = input(f"Choose template (1-{len(template_list)}, default 1): ").strip() or "1"

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(template_list):
            return template_list[idx]
    except ValueError:
        pass

    return template_list[0]


def build_script_with_template(llm_provider, topic: str, template_key: str, tone: str, word_range: tuple) -> str:
    """Generate script using specified template"""
    template = PODCAST_TEMPLATES[template_key]

    prompt = f"""{template['system_prompt']}

Topic: {topic}
Tone: {tone}
Target length: {word_range[0]}-{word_range[1]} words

Generate the complete podcast script following the template structure."""

    response = llm_provider.generate_text(prompt)
    return response


def build_show_notes_with_template(llm_provider, script: str, template_key: str) -> str:
    """Generate show notes tailored to template format"""
    template = PODCAST_TEMPLATES[template_key]

    prompt = f"""Based on this {template['name']} podcast script, create concise show notes.

Include:
- Brief episode summary (2-3 sentences)
- Key topics covered
- Main takeaways or insights
- Template format used

Script:
{script}

Generate the show notes:"""

    response = llm_provider.generate_text(prompt)
    return response


def main():
    """Template-driven podcast generation"""
    print("\n" + "="*70)
    print("Step 27: Stronger Podcast Templates")
    print("="*70)

    # Detect providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available. Set OPENAI_API_KEY or GOOGLE_API_KEY")
        return

    # Choose template
    template_key = get_template_choice()
    template = PODCAST_TEMPLATES[template_key]

    print(f"\n[OK] Selected template: {template['name']}")
    print(f"    {template['description']}")

    # Choose providers (simplified - just use first available for both)
    provider_name = list(available.keys())[0]
    provider_config = ProviderConfig(
        llm_provider=provider_name,
        tts_provider=provider_name
    )

    llm_provider = create_llm_provider(provider_config)
    tts_provider = create_tts_provider(provider_config)

    print(f"\n[OK] Using provider: {provider_name}")

    # Get episode settings
    topic = input("\nEnter episode topic: ").strip()
    if not topic:
        topic = f"{template['name']} Demo"

    tone = get_user_input("Choose tone (casual/professional/educational)", config.DEFAULT_TONE)
    voice = get_user_input(
        f"Choose voice ({'/'.join(tts_provider.available_voices)})",
        tts_provider.available_voices[0]
    )
    length = get_user_input("Choose length (short/medium/long)", config.DEFAULT_LENGTH)

    # Validate
    tone = validate_choice(tone, config.VALID_TONES, "tone")
    voice = validate_choice(voice, set(tts_provider.available_voices), "voice")
    length = validate_choice(length, config.VALID_LENGTHS, "length")
    word_range = get_word_range(length)

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"\n[OK] Episode directory: {episode_dir}")
    print(f"[OK] Template: {template['name']}")

    # Generate script with template
    print(f"\nGenerating {template['name']} script...")
    try:
        script = build_script_with_template(llm_provider, topic, template_key, tone, word_range)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Script generated using {template['name']} template")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes = build_show_notes_with_template(llm_provider, script, template_key)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")
    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nTemplate: {template['name']}"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

    # Generate audio
    audio_file = episode_dir / f"podcast_{voice}.mp3"
    print(f"\nGenerating audio...")
    try:
        generate_audio(tts_provider, script, voice, audio_file)
        print(f"[OK] Audio generated")
    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")

    # Save metadata
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "template": {
            "key": template_key,
            "name": template['name'],
            "description": template['description']
        },
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "template_used": template['name']
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 27 Complete: Template-Based Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Template: {template['name']}")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - script.txt ({template['name']} format)")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")


if __name__ == "__main__":
    main()
