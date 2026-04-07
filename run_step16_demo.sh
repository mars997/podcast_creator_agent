#!/bin/bash
# Demo script to show Step 16 output without requiring API calls

cd "$(dirname "$0")"

topic="step16_demo"
timestamp=$(date +"%Y-%m-%d_%H%M%S")
unique_id="${topic}_${timestamp}"

echo "Creating Step 16 demo episode: $unique_id"

# Create episode folder with timestamp
mkdir -p "output/$unique_id/sources"

# Copy source file
cp demo_source.txt "output/$unique_id/sources/source_1_demo_source.txt"

# Create mock metadata.json with episode_id
cat > "output/$unique_id/metadata.json" << EOF
{
  "created_at": "$(date -Iseconds)",
  "episode_id": "$unique_id",
  "topic": "$topic",
  "tone": "educational",
  "voice": "nova",
  "length": "medium",
  "outputs": {
    "episode_dir": "output/$unique_id",
    "script_file": "output/$unique_id/script.txt",
    "show_notes_file": "output/$unique_id/show_notes.txt",
    "audio_file": "output/$unique_id/podcast_nova.mp3"
  }
}
EOF

# Create placeholder files
echo "Mock script content for $unique_id" > "output/$unique_id/script.txt"
echo "Mock show notes for $unique_id" > "output/$unique_id/show_notes.txt"

echo "Created episode folder: output/$unique_id"
ls -la "output/$unique_id"
