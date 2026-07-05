from __future__ import annotations

import json
import os
import random
from typing import Any

from models.schemas import BedtimeStory, ChildProfile, DollCharacter, StoryScene
from services.safety import is_story_safe

STORY_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "luna-starlight": [
        {
            "title": "A Star for {child}",
            "scene_1_title": "The Moonlit Invitation",
            "scene_1": (
                "On a quiet evening, {child} looked out the window and noticed one star "
                "twinkling brighter than all the rest. It seemed to wink — just for {child}. "
                "That was when Luna Starlight appeared, her silver dress shimmering like moonbeams."
            ),
            "scene_1_caption": "{child} meets Luna beneath a glowing moon",
            "scene_2_title": "Worries Into Stardust",
            "scene_2": (
                "Luna held out her hand. \"Every brave explorer like you carries little worries "
                "sometimes,\" she whispered. \"Shall we turn yours into stardust?\" Together they "
                "blew wishes into the night sky, and {child} felt lighter with every sparkle."
            ),
            "scene_2_caption": "Luna and {child} scatter worries as golden stars",
            "scene_3_title": "The Coziest Constellation",
            "scene_3": (
                "Luna showed {child} a brand-new constellation shaped like a smiling face — "
                "with a spot right in the middle for {child}'s name. \"The sky remembers every "
                "kind heart,\" Luna said softly. \"And yours shines the brightest tonight.\""
            ),
            "scene_3_caption": "A constellation forms with {child}'s name among the stars",
            "moral": "You are braver than you know, and the night is always on your side.",
        },
        {
            "title": "{child} and Luna's Dream Boat",
            "scene_1_title": "A Boat Made of Clouds",
            "scene_1": (
                "When {child} tucked in under the blanket, Luna Starlight arrived on a tiny boat "
                "made of the softest cloud. \"Climb aboard, {child},\" she giggled. "
                "\"Tonight we sail the Moonlit Meadow.\""
            ),
            "scene_1_caption": "{child} boards Luna's cloud boat under the moon",
            "scene_2_title": "The Meadow of Yawns",
            "scene_2": (
                "They drifted past drowsy fireflies and flowers that closed their petals one by one. "
                "Luna hummed a lullaby, and {child} hummed along. Even the crickets slowed their "
                "song to match {child}'s gentle breathing."
            ),
            "scene_2_caption": "Fireflies guide the boat through a sleepy meadow",
            "scene_3_title": "Safe Harbor in Bed",
            "scene_3": (
                "The cloud boat sailed right back to {child}'s pillow. Luna tucked the blanket "
                "around {child}'s shoulders. \"I'll keep watch from the moon,\" she promised. "
                "\"Sweet dreams, little star.\""
            ),
            "scene_3_caption": "Luna tucks {child} in as the moon glows softly",
            "moral": "Rest is a wonderful adventure too — and you deserve every peaceful moment.",
        },
    ],
    "sunny-meadow": [
        {
            "title": "Sunny Meadow's Gift for {child}",
            "scene_1_title": "A Knock at the Garden Gate",
            "scene_1": (
                "While {child} was getting ready for bed, a tiny golden glow appeared at the window. "
                "It was Sunny Meadow, carrying a basket of the sweetest buttercups. "
                "\"I heard someone wonderful lives here,\" Sunny beamed. \"Is that you, {child}?\""
            ),
            "scene_1_caption": "Sunny Meadow arrives with a basket of flowers for {child}",
            "scene_2_title": "Three Thank-Yous",
            "scene_2": (
                "Sunny taught {child} a bedtime game: name three good things from today. "
                "{child} thought carefully and shared the happiest moments. With each one, "
                "a new flower bloomed in Sunny's basket, filling the room with warmth."
            ),
            "scene_2_caption": "Flowers bloom as {child} shares happy memories",
            "scene_3_title": "A Meadow on the Pillow",
            "scene_3": (
                "Sunny placed the brightest buttercup on {child}'s pillow. \"This meadow travels "
                "wherever you go,\" she said. \"And it will always remember the kindness of {child}.\""
            ),
            "scene_3_caption": "A golden buttercup rests beside {child}'s pillow",
            "moral": "Your kindness makes the whole world bloom a little brighter.",
        },
    ],
    "captain-whiskers": [
        {
            "title": "Captain Whiskers and the Brave {child}",
            "scene_1_title": "All Aboard the Pillow Fort",
            "scene_1": (
                "Captain Whiskers appeared at the foot of {child}'s bed wearing the tiniest sailor hat. "
                "\"Ahoy, {child}!\" he called in his bravest whisper. \"I've sailed seven seas of "
                "blankets looking for the most courageous first mate. That's you!\""
            ),
            "scene_1_caption": "Captain Whiskers salutes {child} from a pillow fort ship",
            "scene_2_title": "The Storm of Silly Sounds",
            "scene_2": (
                "A pretend storm rattled the pillow fort — just the wind outside, nothing scary at all. "
                "Captain Whiskers stood tall beside {child}. \"Every great captain feels a little "
                "nervous sometimes,\" he admitted. \"But together? We're unstoppable.\""
            ),
            "scene_2_caption": "{child} and Captain Whiskers face the storm side by side",
            "scene_3_title": "Treasure Found: Cozy Sleep",
            "scene_3": (
                "The storm passed, and Captain Whiskers declared the greatest treasure of all: "
                "a cozy bed and a brave heart. He curled up at {child}'s feet, purring like a tiny engine. "
                "\"Sweet sailing, {child}. Dream of golden shores.\""
            ),
            "scene_3_caption": "Captain Whiskers curls up as {child} drifts to sleep",
            "moral": "Being brave doesn't mean never feeling scared — it means trying anyway.",
        },
    ],
    "princess-ruby": [
        {
            "title": "Princess Ruby and the Crown of {child}",
            "scene_1_title": "A Royal Visit",
            "scene_1": (
                "A gentle knock echoed through {child}'s room — tap, tap, tap, like a fairy-tale drum. "
                "Princess Ruby stepped through a shimmer of rose-colored light. \"I've come to meet "
                "{child},\" she said with a warm smile. \"Legends speak of a child whose heart shines "
                "like a ruby.\""
            ),
            "scene_1_caption": "Princess Ruby greets {child} in a rose-gold glow",
            "scene_2_title": "The Mirror of Truth",
            "scene_2": (
                "Ruby held up a magic mirror that didn't show appearances — only kindness. "
                "In it, {child} saw all the wonderful things they had done: sharing, helping, laughing. "
                "\"See?\" Ruby whispered. \"You were royal all along, {child}.\""
            ),
            "scene_2_caption": "The mirror reveals {child}'s kindness shining bright",
            "scene_3_title": "A Crown of Dreams",
            "scene_3": (
                "Ruby placed a crown of soft starlight on {child}'s head — light as a feather, "
                "warm as a hug. \"Wear this in your dreams tonight,\" she said. \"The Crystal Rose "
                "Kingdom celebrates {child}.\""
            ),
            "scene_3_caption": "{child} wears a crown of starlight in a magical kingdom",
            "moral": "The bravest thing you can be is exactly who you are.",
        },
    ],
    "cosmo-cloud": [
        {
            "title": "{child}'s Star Map with Cosmo Cloud",
            "scene_1_title": "A Friend From the Sky",
            "scene_1": (
                "As {child} lay in bed, a fluffy cloud floated through the open window — but it wasn't "
                "ordinary at all. Cosmo Cloud had button eyes and the kindest smile. \"Hello, {child},\" "
                "Cosmo whispered. \"Want to map the stars together?\""
            ),
            "scene_1_caption": "Cosmo Cloud floats in to visit {child}",
            "scene_2_title": "Drawing Constellations",
            "scene_2": (
                "Cosmo pulled out a glowing star map. Together, {child} and Cosmo connected the dots "
                "in the ceiling, making new constellations: a dragon, a heart, and one that looked "
                "just like {child}'s favorite thing. \"The universe loves your imagination,\" Cosmo said."
            ),
            "scene_2_caption": "{child} and Cosmo draw glowing constellations together",
            "scene_3_title": "Floating Into Sleep",
            "scene_3": (
                "Cosmo grew soft and pillow-like, cradling {child} like a gentle hammock among the stars. "
                "\"I'll orbit your dreams all night,\" Cosmo promised. \"And when morning comes, "
                "I'll still be right here beside you, {child}.\""
            ),
            "scene_3_caption": "Cosmo cradles {child} among a sky full of stars",
            "moral": "Your dreams are as vast and wonderful as the whole universe.",
        },
    ],
}


def _format_template(template: dict[str, str], child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    child_name = child.display_name()
    context = {"child": child_name, "doll": doll.name}

    def fmt(value: str) -> str:
        return value.format(**context)

    scenes = [
        StoryScene(
            title=fmt(template["scene_1_title"]),
            text=fmt(template["scene_1"]),
            illustration_caption=fmt(template["scene_1_caption"]),
        ),
        StoryScene(
            title=fmt(template["scene_2_title"]),
            text=fmt(template["scene_2"]),
            illustration_caption=fmt(template["scene_2_caption"]),
        ),
        StoryScene(
            title=fmt(template["scene_3_title"]),
            text=fmt(template["scene_3"]),
            illustration_caption=fmt(template["scene_3_caption"]),
        ),
    ]

    return BedtimeStory(
        title=fmt(template["title"]),
        child_name=child_name,
        doll_name=doll.name,
        doll_id=doll.id,
        scenes=scenes,
        moral=fmt(template["moral"]),
        reading_time_minutes=3,
        generated_by="template",
    )


def generate_template_story(child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    templates = STORY_TEMPLATES.get(doll.id, STORY_TEMPLATES["luna-starlight"])
    template = random.choice(templates)
    return _format_template(template, child, doll)


def _build_llm_prompt(child: ChildProfile, doll: DollCharacter) -> str:
    age_note = f"They are {child.age} years old." if child.age else ""
    return f"""Write a short, gentle bedtime story for a child named {child.display_name()}. {age_note}

The story stars the doll character "{doll.name}" from the world of {doll.world}.
Character personality: {", ".join(doll.personality)}.
Themes to weave in: {", ".join(doll.themes)}.
Voice style: {doll.voice_style}.

Requirements:
- Use the child's name naturally 4-6 times throughout the story
- Exactly 3 short scenes, each 2-3 sentences
- Age-appropriate, calming, no scary content, no violence
- End with a gentle moral and bedtime feeling
- The story is a sales preview — make the doll feel magical and lovable

Respond ONLY with valid JSON in this exact shape:
{{
  "title": "story title",
  "scenes": [
    {{"title": "scene title", "text": "scene text", "illustration_caption": "short image caption"}},
    {{"title": "...", "text": "...", "illustration_caption": "..."}},
    {{"title": "...", "text": "...", "illustration_caption": "..."}}
  ],
  "moral": "one gentle sentence"
}}"""


def _parse_llm_response(payload: dict[str, Any], child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    scenes = [
        StoryScene(
            title=scene["title"],
            text=scene["text"],
            illustration_caption=scene.get("illustration_caption", scene["title"]),
        )
        for scene in payload["scenes"]
    ]
    story = BedtimeStory(
        title=payload["title"],
        child_name=child.display_name(),
        doll_name=doll.name,
        doll_id=doll.id,
        scenes=scenes,
        moral=payload.get("moral", ""),
        reading_time_minutes=3,
        generated_by="openai",
    )
    if not is_story_safe(story.full_text()):
        raise ValueError("Generated story failed safety check")
    return story


def generate_openai_story(child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package not installed") from exc

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You write warm, age-appropriate bedtime stories for children. "
                    "Always respond with valid JSON only. Never include frightening content."
                ),
            },
            {"role": "user", "content": _build_llm_prompt(child, doll)},
        ],
        temperature=0.8,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response from OpenAI")

    payload = json.loads(content)
    return _parse_llm_response(payload, child, doll)


def generate_story(child: ChildProfile, doll: DollCharacter, prefer_ai: bool = True) -> BedtimeStory:
    if prefer_ai and os.getenv("OPENAI_API_KEY"):
        try:
            return generate_openai_story(child, doll)
        except Exception:
            pass
    return generate_template_story(child, doll)
