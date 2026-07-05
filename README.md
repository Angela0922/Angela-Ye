# Apple Park Kids — Personalized Story Chat

**AI chatbot for parents** — tell us about your child, get matched with the perfect [Apple Park Kids](https://appleparkkids.com) organic cotton doll (with product photo & shop link), and receive a personalized bedtime story starring your little one.

> *"Chat about your child. We'll find their Apple Park friend and write a bedtime story just for them."*

## How it works

1. Parent **chats** about their child (name, age, interests, personality, bedtime routines)
2. App **recommends the best-matching doll** with product image and shop link
3. App generates a **3-scene bedtime story** set in Apple Park
4. Optional **narrated video** (MP4) with voice narration
5. **Shop CTA** links directly to the doll's product page on appleparkkids.com

## Every doll has a story

| Doll | Personality | Shop |
|------|-------------|------|
| **Alex** | Curious critter explorer | [Shop Alex](https://appleparkkids.com/products/park-friends-alex) |
| **Ella** | Tea party host & friend-gatherer | [Shop Ella](https://appleparkkids.com/products/organic-best-friends-ella) |
| **Grady** | Helpful hero who cheers up friends | [Shop Grady](https://appleparkkids.com/products/grady-in-caramel) |
| **Gwen** | Musical songbird & lullaby maker | [Shop Gwen](https://appleparkkids.com/products/park-friends-gwen) |
| **Levi** | Sandcastle architect extraordinaire | [Shop Levi](https://appleparkkids.com/products/levi-in-sage) |
| **Luke** | Gentle playground pal | [Shop Luke](https://appleparkkids.com/products/luke-in-marine) |
| **Mia** | Peek-a-boo surprise lover | [Shop Mia](https://appleparkkids.com/products/mia-in-dusty-rose) |
| **Paloma** | Kind sharer & turn-taker | [Shop Paloma](https://appleparkkids.com/products/park-friends-paloma) |
| **Wren** | Cozy story-time friend | [Shop Wren](https://appleparkkids.com/products/apple-park-kids-wren) |

5. **Shop CTA** links directly to the doll's product page on appleparkkids.com

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

### Generate videos for all dolls at once

```bash
python3 scripts/generate_all_videos.py --child-name Emma
```

Videos are cached in `assets/videos/`.

### Optional: AI-unique stories

```bash
cp .env.example .env
# Add OPENAI_API_KEY for GPT-generated unique stories
```

## Features

| Feature | Default (no API key) | With OpenAI |
|---------|---------------------|-------------|
| Conversational parent chat | ✓ | ✓ |
| Smart doll matching + product image | ✓ | ✓ (AI-enhanced) |
| All 9 Apple Park Kids dolls | ✓ | ✓ |
| Child name personalization | ✓ | ✓ |
| Narrated video story (MP4) | ✓ | ✓ |
| Real product URLs & pricing | ✓ | ✓ |
| Unique AI-written stories | — | ✓ |
| DALL-E scene illustrations | — | ✓ |

## Project structure

```
├── app.py                          # Streamlit chat UI
├── data/
│   ├── characters.json             # All 9 Apple Park Kids dolls
│   └── story_templates.json        # Per-doll bedtime story templates
├── services/
│   ├── chatbot.py                  # Parent conversation orchestrator
│   ├── doll_recommender.py         # Match child profile → best doll
│   ├── story_generator.py          # Story engine (templates + OpenAI)
│   ├── video_story.py              # MP4 builder (slides + narration)
│   ├── scene_renderer.py           # Illustrated slide images (Pillow)
│   └── narrator.py                 # Text-to-speech (gTTS)
├── scripts/
│   └── generate_all_videos.py      # Batch-generate all doll videos
└── assets/videos/                  # Cached MP4 outputs
```

## Requirements

- Python 3.10+
- **ffmpeg** (for video assembly)
- Internet access (for gTTS narration)

## License

MIT — see [LICENSE](LICENSE).
