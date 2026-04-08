from core.provider_setup import initialize_providers
from core.content_generation import build_script

# Initialize providers
llm_provider, _ = initialize_providers()

topic = input("Enter a podcast topic: ").strip()

if not topic:
    raise ValueError("Topic cannot be empty.")

# Generate script using core module
script = build_script(
    llm_provider,
    topic,
    tone="casual",
    word_range="300 to 500 words"
)

print("\n" + "=" * 60)
print("PODCAST SCRIPT")
print("=" * 60)
print(script)
print("=" * 60)