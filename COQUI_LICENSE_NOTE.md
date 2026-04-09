# Coqui TTS License Information

## License Type

Coqui XTTS v2 is released under the **Coqui Public Model License (CPML)**.

### Non-Commercial Use (Default)

This implementation uses Coqui TTS under the **non-commercial CPML license**.

**You can use it for:**
- Personal projects
- Research
- Education
- Testing and demos
- Non-profit organizations

**License terms:** https://coqui.ai/cpml

### Commercial Use

If you need to use this for commercial purposes (business, monetization, client work), you must:

1. Purchase a commercial license from Coqui
2. Contact: licensing@coqui.ai
3. Update the code to use your commercial license

## Implementation Note

The code automatically accepts the non-commercial CPML terms by setting:
```python
os.environ["COQUI_TOS_AGREED"] = "1"
```

This is equivalent to manually typing "y" when prompted with:
```
> I agree to the terms of the non-commercial CPML: https://coqui.ai/cpml - [y/n]
```

## Your Responsibility

By using this voice cloning feature, you agree to:
- Use it only for non-commercial purposes (unless you have a commercial license)
- Follow the CPML terms: https://coqui.ai/cpml
- Not use it for illegal or harmful purposes
- Respect voice rights and obtain consent before cloning someone's voice

## Alternative Solutions

If you need commercial voice cloning without licensing fees, consider:
- ElevenLabs (paid per use, includes commercial rights)
- Resemble AI (paid, commercial-friendly)
- Play.ht (paid, commercial-friendly)

---

**Summary:** Free for personal/research use. Commercial use requires a license from Coqui.
