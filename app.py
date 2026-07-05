"""Bedtime Story Sales Hook — personalized doll stories for children."""

from __future__ import annotations

import streamlit as st

from models.schemas import ChildProfile
from services.character_loader import get_character, load_characters
from services.illustrator import generate_scene_image, get_scene_image_path, scene_emoji, scene_gradient
from services.safety import is_valid_child_name, sanitize_child_name
from services.story_generator import generate_story

st.set_page_config(
    page_title="DreamDoll Stories — A Bedtime Preview Just for Your Child",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;700&family=Nunito:wght@400;600;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #1a1033 0%, #2d1b4e 35%, #1a1033 100%);
    }

    .hero-title {
        font-family: 'Fraunces', serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #fff8f0;
        line-height: 1.15;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-family: 'Nunito', sans-serif;
        font-size: 1.15rem;
        color: #d4c4f0;
        margin-bottom: 1.5rem;
    }

    .hook-badge {
        display: inline-block;
        background: linear-gradient(90deg, #ffd700, #ff9a56);
        color: #1a1033;
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        margin-bottom: 1rem;
        letter-spacing: 0.03em;
    }

    .doll-card {
        background: rgba(255, 255, 255, 0.06);
        border: 2px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.2s ease;
        cursor: pointer;
        min-height: 200px;
    }

    .doll-card:hover {
        border-color: rgba(255, 215, 0, 0.5);
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }

    .doll-card.selected {
        border-color: #ffd700;
        background: rgba(255, 215, 0, 0.12);
        box-shadow: 0 0 24px rgba(255, 215, 0, 0.2);
    }

    .doll-emoji {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    .doll-name {
        font-family: 'Fraunces', serif;
        font-size: 1.2rem;
        color: #fff8f0;
        font-weight: 700;
    }

    .doll-tagline {
        font-family: 'Nunito', sans-serif;
        font-size: 0.8rem;
        color: #c9b8e8;
        margin-top: 0.4rem;
    }

    .scene-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .scene-illustration {
        border-radius: 12px;
        min-height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .scene-title {
        font-family: 'Fraunces', serif;
        font-size: 1.3rem;
        color: #ffd700;
        margin-bottom: 0.5rem;
    }

    .scene-text {
        font-family: 'Nunito', sans-serif;
        font-size: 1.05rem;
        color: #e8dff5;
        line-height: 1.7;
    }

    .cta-box {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 154, 86, 0.15));
        border: 2px solid rgba(255, 215, 0, 0.4);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin-top: 1.5rem;
    }

    .cta-title {
        font-family: 'Fraunces', serif;
        font-size: 1.6rem;
        color: #fff8f0;
        margin-bottom: 0.5rem;
    }

    .cta-text {
        font-family: 'Nunito', sans-serif;
        color: #d4c4f0;
        font-size: 1rem;
    }

    .price-tag {
        font-family: 'Fraunces', serif;
        font-size: 2rem;
        color: #ffd700;
        font-weight: 700;
    }

    div[data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero():
    st.markdown('<div class="hook-badge">✨ FREE PREVIEW — NO PURCHASE REQUIRED</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title">A bedtime story starring<br>your child & their new best friend</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">Enter your child\'s name, pick a DreamDoll character, '
        "and watch a magical illustrated story appear — starring them. "
        "It's our way of saying: this doll was meant for your little one.</div>",
        unsafe_allow_html=True,
    )


def render_doll_picker(characters: list, selected_id: str | None) -> str | None:
    st.markdown("#### Choose your DreamDoll companion")
    cols = st.columns(len(characters))
    picked = selected_id

    for col, doll in zip(cols, characters):
        is_selected = doll.id == selected_id
        card_class = "doll-card selected" if is_selected else "doll-card"
        with col:
            st.markdown(
                f'<div class="{card_class}">'
                f'<div class="doll-emoji">{doll.emoji}</div>'
                f'<div class="doll-name">{doll.name}</div>'
                f'<div class="doll-tagline">{doll.tagline}</div>'
                f'<div style="color:#ffd700;font-weight:700;margin-top:0.6rem;">${doll.price:.2f}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
            if st.button(f"Select {doll.name}", key=f"pick_{doll.id}", use_container_width=True):
                picked = doll.id

    return picked


def render_story(story, doll, generate_images: bool):
    st.markdown("---")
    st.markdown(f"## {story.title}")
    st.caption(
        f"~{story.reading_time_minutes} min read · Starring **{story.child_name}** & **{story.doll_name}**"
    )

    for index, scene in enumerate(story.scenes):
        image_path = get_scene_image_path(story, scene, index)
        if generate_images and image_path is None:
            with st.spinner(f"Painting scene {index + 1}..."):
                image_path = generate_scene_image(story, scene, doll, index)

        gradient = scene_gradient(doll, index)
        emoji = scene_emoji(doll, index)

        st.markdown('<div class="scene-card">', unsafe_allow_html=True)

        if image_path:
            st.image(str(image_path), caption=scene.illustration_caption, use_container_width=True)
        else:
            st.markdown(
                f'<div class="scene-illustration" style="background:{gradient};">'
                f'<span title="{scene.illustration_caption}">{emoji}</span></div>',
                unsafe_allow_html=True,
            )
            st.caption(scene.illustration_caption)

        st.markdown(f'<div class="scene-title">{scene.title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="scene-text">{scene.text}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if story.moral:
        st.info(f"**Sweet dreams, {story.child_name}.** {story.moral}")


def render_cta(doll, child_name: str):
    st.markdown(
        f'<div class="cta-box">'
        f'<div class="cta-title">{child_name} loved this story?</div>'
        f'<div class="cta-text">Bring <strong>{doll.name}</strong> home tonight — '
        f"the doll who already knows your child's name.</div>"
        f'<div class="price-tag">${doll.price:.2f}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            f"🛒 Add {doll.name} to Cart — ${doll.price:.2f}",
            doll.purchase_url,
            use_container_width=True,
            type="primary",
        )
        st.caption("Free shipping on orders over $50 · 30-day happiness guarantee")


def main():
    render_hero()

    characters = load_characters()

    if "selected_doll_id" not in st.session_state:
        st.session_state.selected_doll_id = characters[0].id
    if "story" not in st.session_state:
        st.session_state.story = None

    col_input, col_doll = st.columns([1, 2])

    with col_input:
        st.markdown("#### Your child's name")
        child_name = st.text_input(
            "Child's first name",
            placeholder="e.g. Emma",
            label_visibility="collapsed",
        )
        child_age = st.number_input("Age (optional)", min_value=1, max_value=12, value=5, step=1)

        generate_images = st.checkbox(
            "Generate AI illustrations (requires OpenAI API key)",
            value=False,
            help="Uses DALL-E to paint custom scenes. Without an API key, beautiful gradient scene cards are shown instead.",
        )

        ai_available = bool(__import__("os").getenv("OPENAI_API_KEY"))
        if ai_available:
            st.caption("✨ AI story generation enabled")
        else:
            st.caption("📖 Using curated story templates (set OPENAI_API_KEY for unique AI stories)")

    with col_doll:
        st.session_state.selected_doll_id = render_doll_picker(
            characters, st.session_state.selected_doll_id
        )

    st.markdown("")
    generate_clicked = st.button(
        "✨ Create My Child's Story",
        type="primary",
        use_container_width=True,
        disabled=not child_name,
    )

    if not child_name:
        st.caption("Enter your child's name above to unlock their personalized story.")

    if generate_clicked:
        cleaned = sanitize_child_name(child_name)
        if not is_valid_child_name(cleaned):
            st.error("Please enter a valid first name (letters only, 2–32 characters).")
        else:
            doll = get_character(st.session_state.selected_doll_id)
            if doll is None:
                st.error("Please select a DreamDoll character.")
            else:
                child = ChildProfile(name=cleaned, age=child_age)
                with st.spinner(f"Weaving a story for {child.display_name()} and {doll.name}..."):
                    st.session_state.story = generate_story(child, doll)

    if st.session_state.story:
        doll = get_character(st.session_state.story.doll_id)
        if doll:
            render_story(st.session_state.story, doll, generate_images)
            render_cta(doll, st.session_state.story.child_name)

            with st.expander("Share or save this story"):
                st.download_button(
                    "Download story as text",
                    st.session_state.story.full_text(),
                    file_name=f"{st.session_state.story.child_name}-{doll.id}-bedtime-story.txt",
                    mime="text/plain",
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
