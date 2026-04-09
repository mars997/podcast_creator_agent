"""
TTS Script Optimizer

Transforms written text into spoken-friendly text optimized for TTS engines.
Makes scripts sound more natural and conversational.
"""

import re
from typing import List
from core.voice_styles import VoiceStyle, SentenceLength, PunctuationStyle, Pacing


class TTSScriptOptimizer:
    """
    Optimizes scripts for better TTS delivery.

    Techniques:
    - Sentence length control
    - Strategic pause insertion
    - Contraction application
    - Interjection addition
    - Filler word injection (when appropriate)
    - Emphasis via punctuation
    """

    # Common contractions
    CONTRACTIONS = {
        "cannot": "can't",
        "will not": "won't",
        "shall not": "shan't",
        "would not": "wouldn't",
        "should not": "shouldn't",
        "could not": "couldn't",
        "do not": "don't",
        "does not": "doesn't",
        "did not": "didn't",
        "is not": "isn't",
        "are not": "aren't",
        "was not": "wasn't",
        "were not": "weren't",
        "has not": "hasn't",
        "have not": "haven't",
        "had not": "hadn't",
        "it is": "it's",
        "he is": "he's",
        "she is": "she's",
        "that is": "that's",
        "there is": "there's",
        "what is": "what's",
        "who is": "who's",
        "they are": "they're",
        "we are": "we're",
        "you are": "you're",
        "I am": "I'm",
        "I will": "I'll",
        "you will": "you'll",
        "they will": "they'll",
        "we will": "we'll",
        "I have": "I've",
        "you have": "you've",
        "they have": "they've",
        "we have": "we've"
    }

    # Interjections for natural flow
    INTERJECTIONS = [
        "Well, ",
        "So, ",
        "Now, ",
        "Okay, ",
        "Alright, ",
        "Look, ",
        "Listen, ",
        "Hey, ",
        "Right, ",
        "Actually, "
    ]

    # Filler words (use sparingly)
    FILLERS = [
        "you know",
        "I mean",
        "like",
        "basically",
        "essentially"
    ]

    def optimize(self, text: str, voice_style: VoiceStyle) -> str:
        """
        Main optimization pipeline

        Args:
            text: Original script text
            voice_style: Voice style with optimization hints

        Returns:
            TTS-optimized script
        """
        # 1. Clean up existing formatting
        text = self._clean_text(text)

        # 2. Apply sentence length optimization
        text = self._optimize_sentence_length(text, voice_style.sentence_length)

        # 3. Apply contractions
        if voice_style.use_contractions:
            text = self._apply_contractions(text)

        # 4. Add interjections
        if voice_style.use_interjections:
            text = self._add_interjections(text, voice_style.pacing)

        # 5. Add strategic pauses
        text = self._add_strategic_pauses(text, voice_style.punctuation_style)

        # 6. Add filler words (if appropriate)
        if voice_style.use_filler_words:
            text = self._add_fillers(text)

        # 7. Pacing markers
        text = self._add_pacing_markers(text, voice_style.pacing)

        # 8. Emphasis via punctuation
        text = self._add_punctuation_emphasis(text)

        return text

    def _clean_text(self, text: str) -> str:
        """Remove markdown and clean formatting"""
        # Remove markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
        text = re.sub(r'`(.+?)`', r'\1', text)  # Code
        text = re.sub(r'#+ ', '', text)  # Headers

        # Clean multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Clean multiple periods
        text = re.sub(r'\.{4,}', '...', text)

        return text.strip()

    def _optimize_sentence_length(self, text: str, target_length: SentenceLength) -> str:
        """
        Split long sentences into shorter ones for better TTS pacing

        Args:
            text: Input text
            target_length: SHORT (5-10), MEDIUM (10-15), LONG (15-20) words

        Returns:
            Text with optimized sentence lengths
        """
        max_words = {
            SentenceLength.SHORT: 10,
            SentenceLength.MEDIUM: 15,
            SentenceLength.LONG: 20
        }.get(target_length, 15)

        sentences = re.split(r'([.!?])\s+', text)
        optimized = []

        i = 0
        while i < len(sentences):
            sentence = sentences[i]

            # If this is punctuation, append to previous
            if sentence in '.!?':
                if optimized:
                    optimized[-1] += sentence
                i += 1
                continue

            words = sentence.split()

            # If sentence is short enough, keep it
            if len(words) <= max_words:
                optimized.append(sentence)
                i += 1
                continue

            # Split long sentence at natural break points
            split_sentences = self._split_at_natural_breaks(sentence, max_words)
            optimized.extend(split_sentences)

            i += 1

        return ' '.join(optimized)

    def _split_at_natural_breaks(self, sentence: str, max_words: int) -> List[str]:
        """Split sentence at commas, conjunctions, or mid-point"""
        # Try to split at comma
        if ',' in sentence:
            parts = sentence.split(',')
            result = []
            current = ""

            for part in parts:
                if not current:
                    current = part
                elif len((current + ',' + part).split()) <= max_words:
                    current += ',' + part
                else:
                    result.append(current.strip() + '.')
                    current = part

            if current:
                result.append(current.strip() + '.')

            return result

        # No comma - split at mid-point
        words = sentence.split()
        mid = max_words
        part1 = ' '.join(words[:mid]) + '.'
        part2 = ' '.join(words[mid:]) + '.'

        return [part1, part2]

    def _apply_contractions(self, text: str) -> str:
        """Apply common contractions to sound more natural"""
        for full, contracted in self.CONTRACTIONS.items():
            # Case-insensitive replacement with word boundaries
            pattern = r'\b' + re.escape(full) + r'\b'
            text = re.sub(pattern, contracted, text, flags=re.IGNORECASE)

        return text

    def _add_interjections(self, text: str, pacing: Pacing) -> str:
        """Add conversational interjections at sentence starts"""
        # More interjections for faster pacing
        frequency = {
            Pacing.SLOW: 0.1,  # 10% of sentences
            Pacing.MODERATE: 0.15,  # 15%
            Pacing.FAST: 0.25,  # 25%
            Pacing.RAPID: 0.35  # 35%
        }.get(pacing, 0.15)

        sentences = re.split(r'([.!?])\s+', text)
        result = []

        import random
        random.seed(42)  # Deterministic

        for i, part in enumerate(sentences):
            if part in '.!?':
                result.append(part)
                continue

            # Add interjection with probability
            if random.random() < frequency and not part.startswith(tuple(self.INTERJECTIONS)):
                interjection = random.choice(self.INTERJECTIONS)
                result.append(interjection + part)
            else:
                result.append(part)

        return ' '.join(result)

    def _add_strategic_pauses(self, text: str, style: PunctuationStyle) -> str:
        """Add pauses using ellipses and em dashes"""
        if style == PunctuationStyle.MINIMAL:
            return text

        if style == PunctuationStyle.DRAMATIC:
            # Add more dramatic pauses
            # Replace some commas with ellipses
            text = re.sub(r',\s+(and|but|or)\s+', r'... \\1 ', text)

            # Add em dashes for interruptions (occasionally)
            text = re.sub(r'\s+(however|nevertheless|moreover)\s+', r' — \\1 — ', text)

        return text

    def _add_fillers(self, text: str) -> str:
        """Add filler words sparingly for very casual speech"""
        import random
        random.seed(42)

        sentences = text.split('. ')
        result = []

        for sentence in sentences:
            # Add filler word with 10% probability
            if random.random() < 0.1:
                filler = random.choice(self.FILLERS)
                # Insert in middle of sentence
                words = sentence.split()
                if len(words) > 5:
                    insert_pos = len(words) // 2
                    words.insert(insert_pos, filler + ',')
                    sentence = ' '.join(words)

            result.append(sentence)

        return '. '.join(result)

    def _add_pacing_markers(self, text: str, pacing: Pacing) -> str:
        """Add pacing hints via punctuation"""
        if pacing == Pacing.SLOW:
            # Add more periods for longer pauses
            text = text.replace('!', '.')
            text = text.replace('? ', '.\n\n')  # Longer pause after questions

        elif pacing == Pacing.RAPID:
            # Replace some periods with commas for flow
            sentences = text.split('. ')
            if len(sentences) > 3:
                # Connect some sentences
                for i in range(0, len(sentences) - 1, 3):
                    if i + 1 < len(sentences):
                        sentences[i] = sentences[i] + ','

            text = ' '.join(sentences)

        return text

    def _add_punctuation_emphasis(self, text: str) -> str:
        """Add emphasis via punctuation where appropriate"""
        # Key words that often need emphasis
        emphasis_words = [
            'important', 'critical', 'essential', 'key', 'vital',
            'never', 'always', 'must', 'cannot', 'absolutely'
        ]

        for word in emphasis_words:
            # Add exclamation if word appears mid-sentence
            pattern = r'\b(' + word + r')\b(?![\.\!\?])'
            text = re.sub(pattern, r'\1!', text, flags=re.IGNORECASE)

        return text

    def optimize_for_multi_character(self, script: str, voice_styles: dict) -> str:
        """
        Optimize multi-character script with per-character voice styles

        Args:
            script: Script with speaker labels (SPEAKER: dialogue)
            voice_styles: Dict mapping speaker name to VoiceStyle

        Returns:
            Optimized script with per-speaker optimization
        """
        lines = script.split('\n')
        optimized_lines = []

        for line in lines:
            # Parse speaker label
            match = re.match(r'^([A-Z_]+):\s*(.+)$', line)

            if match:
                speaker, dialogue = match.groups()

                # Get voice style for this speaker
                voice_style = voice_styles.get(speaker)

                if voice_style:
                    # Optimize dialogue for this speaker's style
                    optimized_dialogue = self.optimize(dialogue, voice_style)
                    optimized_lines.append(f"{speaker}: {optimized_dialogue}")
                else:
                    # Keep original if no style
                    optimized_lines.append(line)
            else:
                # Non-dialogue line
                optimized_lines.append(line)

        return '\n'.join(optimized_lines)


def optimize_script(text: str, voice_style: VoiceStyle) -> str:
    """Convenience function for script optimization"""
    optimizer = TTSScriptOptimizer()
    return optimizer.optimize(text, voice_style)
