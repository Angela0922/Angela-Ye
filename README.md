# DreamDoll Bedtime Stories

**AI-generated, child-name-aware bedtime stories** featuring DreamDoll characters — a sales hook that lets parents preview a personalized illustrated story starring their child and the doll they're about to buy.

> *"Hype your child's name. Get a short illustrated story starring the doll you are about to buy."*

## How it works

1. Parent enters their **child's name** (and optional age)
2. They **pick a DreamDoll character** from the catalog
3. The app generates a **3-scene bedtime story** personalized with the child's name
4. Each scene shows an **illustration** (gradient cards by default, or DALL-E when enabled)
5. A **purchase CTA** closes the loop: *"Bring [Doll] home tonight"*

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: enable AI-generated unique stories + illustrations
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Launch the sales-hook demo
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Features

| Feature | Without API key | With `OPENAI_API_KEY` |
|---------|----------------|----------------------|
| Personalized child name | Yes | Yes |
| Doll character stories | Curated templates | Unique AI stories |
| Scene illustrations | Gradient + emoji cards | DALL-E watercolor art |
| Purchase CTA | Yes | Yes |
| Child-safe content | Template + safety filters | Template fallback + filters |

## Doll characters

Five launch characters live in `data/characters.json`:

| Character | Theme | Price |
|-----------|-------|-------|
| Luna Starlight | Dreams & moonlit calm | $34.99 |
| Sunny Meadow | Friendship & gratitude | $32.99 |
| Captain Whiskers | Gentle bravery | $36.99 |
| Princess Ruby | Self-confidence & kindness | $38.99 |
| Cosmo Cloud | Wonder & peaceful sleep | $33.99 |

Edit `data/characters.json` to add your real product SKUs, images, and purchase URLs.

## Project structure

```
├── app.py                      # Streamlit sales-hook UI
├── data/
│   └── characters.json         # Doll catalog (personas, colors, prices)
├── models/
│   └── schemas.py              # Story, Character, ChildProfile types
├── services/
│   ├── character_loader.py     # Load doll catalog
│   ├── story_generator.py      # AI + template story engine
│   ├── illustrator.py          # Scene art (gradient or DALL-E)
│   └── safety.py               # Name validation & content filters
├── assets/scenes/              # Cached DALL-E illustrations
├── requirements.txt
└── .env.example
```

## Integrating with your store

Replace `purchase_url` in each character with your Shopify/WooCommerce product links. The CTA button in `app.py` uses `st.link_button` pointing to that URL.

For embed on a product page, run Streamlit behind a reverse proxy or rebuild the UI in your storefront framework — the story logic in `services/` is framework-agnostic.

## Safety

- Child names are sanitized (letters, spaces, hyphens only)
- Story content is checked against a blocklist
- System prompts enforce age-appropriate, calming bedtime tone
- No child data is persisted by default

## License

MIT — see [LICENSE](LICENSE).
