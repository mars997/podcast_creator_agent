#!/bin/bash

# List of files that need the standard update
files=(
    "step6_podcast_episode.py"
    "step7_custom_podcast.py"
    "step8_podcast_from_source.py"
    "step9_multi_source_podcast.py"
    "step10_podcast_from_urls.py"
    "step11_configurable_podcast.py"
    "step12_hybrid_sources_podcast.py"
    "step13_mixed_sources_podcast.py"
    "step14_episode_metadata.py"
    "step15_episode_index.py"
    "step16_unique_episode_ids.py"
    "step18_regenerate_episode.py"
    "step19_rss_podcast.py"
)

echo "Files to update: ${#files[@]}"
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file NOT FOUND"
    fi
done
