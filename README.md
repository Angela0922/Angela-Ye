# Apple Park Kids — Personalized Video Bedtime Stories

**AI-generated, child-name-aware video stories** for every [Apple Park Kids](https://appleparkkids.com) organic cotton doll — a sales hook that lets parents preview a narrated video story starring their child and the doll they're about to buy.

> *"Hype your child's name. Get a short video story starring the Apple Park Kids doll you are about to buy."*

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

## How it works

1. Parent enters their **child's name**
2. They **pick an Apple Park Kids doll** (all 9 characters)
3. App generates a **3-scene bedtime story** set in Apple Park
4. A **narrated video** is built: illustrated slides + voice narration (MP4)
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
| All 9 Apple Park Kids dolls | ✓ | ✓ |
| Child name personalization | ✓ | ✓ |
| Narrated video story (MP4) | ✓ | ✓ |
| Real product URLs & pricing | ✓ | ✓ |
| Unique AI-written stories | — | ✓ |
| DALL-E scene illustrations | — | ✓ |

## Project structure

```
├── app.py                          # Streamlit demo landing page
├── data/
│   ├── characters.json             # All 9 Apple Park Kids dolls
│   └── story_templates.json        # Per-doll bedtime story templates
├── services/
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
