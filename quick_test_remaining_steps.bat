@echo off
REM Quick test of remaining steps (29-42)

echo Testing Step 29: Grounding Rules
echo 2 | python step29_grounding_rules.py

timeout /t 5

echo Testing Step 30: Segment-Aware
echo 1 | python step30_segment_aware_generation.py

timeout /t 5

echo Testing Step 31: Citations
echo 1 | python step31_citation_support.py

timeout /t 5

echo Testing Step 32: Voice Persona
echo 1 | python step32_voice_persona_system.py

timeout /t 5

echo Testing Step 33: Audio Chunking
python step33_audio_chunking.py < nul

timeout /t 5

echo All quick tests complete
pause
