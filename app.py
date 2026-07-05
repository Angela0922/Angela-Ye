"""Apple Park Kids — personalized video bedtime stories for every doll."""

from __future__ import annotations

import os

import streamlit as st

from models.schemas import ChildProfile
from services.character_loader import get_character, load_characters
from services.illustrator import generate_scene_image, get_scene_image_path, scene_emoji, scene_gradient
from services.safety import is_valid_child_name, sanitize_child_name
from services.story_generator import generate_story
from services.video_story import generate_video_story, get_video_path

st.set_page_config(
    page_title="Apple Park Kids — Personalized Bedtime Video Stories",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;700&family=Nunito:wght@400;600;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #F5F0E8 0%, #E8F0E4 40%, #F5F0E8 100%);
    }

    .hero-title {
        font-family: 'Fraunces', serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: #3D4F3D;
        line-height: 1.15;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-family: 'Nunito', sans-serif;
        font-size: 1.1rem;
        color: #5C6B5C;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }

    .hook-badge {
        display: inline-block;
        background: linear-gradient(90deg, #7D9B76, #A8C5A0);
        color: #fff;
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        margin-bottom: 1rem;
    }

    .doll-card {
        background: #fff;
        border: 2px solid #E0DDD6;
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        min-height: 170px;
        box-shadow: 0 2px 8px rgba(61,79,61,0.06);
    }

    .doll-card.selected {
        border-color: #7D9B76;
        background: #F0F7EE;
        box-shadow: 0 4px 16px rgba(125,155,118,0.2);
    }

    .doll-emoji { font-size: 2.5rem; margin-bottom: 0.3rem; }
    .doll-name {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        color: #3D4F3D;
        font-weight: 700;
    }
    .doll-tagline {
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem;
        color: #6B7B6B;
        margin-top: 0.3rem;
        line-height: 1.3;
    }

    .scene-card {
        background: #fff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #E0DDD6;
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
        color: #5C7A4A;
        margin-bottom: 0.5rem;
    }

    .scene-text {
        font-family: 'Nunito', sans-serif;
        font-size: 1.05rem;
        color: #3D4F3D;
        line-height: 1.7;
    }

    .cta-box {
        background: linear-gradient(135deg, #F0F7EE, #E8F5E9);
        border: 2px solid #7D9B76;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin-top: 1.5rem;
    }

    .cta-title {
        font-family: 'Fraunces', serif;
        font-size: 1.6rem;
        color: #3D4F3D;
    }

    .cta-text {
        font-family: 'Nunito', sans-serif;
        color: #5C6B5C;
        font-size: 1rem;
    }

    .price-tag {
        font-family: 'Fraunces', serif;
        font-size: 2rem;
        color: #5C7A4A;
        font-weight: 700;
    }

    div[data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero():
    st.markdown('<div class="hook-badge">🍎 FREE PREVIEW — EVERY DOLL HAS A STORY</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title">A bedtime video story starring<br>your child & their Apple Park Kids doll</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">Enter your child\'s name, pick one of our organic cotton dolls — '
        "Alex, Ella, Grady, Gwen, Levi, Luke, Mia, Paloma, or Wren — and watch a personalized "
        "video story appear. It's our way of saying: this doll was made for your little one.</div>",
        unsafe_allow_html=True,
    )


def render_doll_picker(characters: list, selected_id: str | None) -> str | None:
    st.markdown("#### Choose your Apple Park Kids doll")
    picked = selected_id
    cols_per_row = 3

    for row_start in range(0, len(characters), cols_per_row):
        row_chars = characters[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, doll in zip(cols, row_chars):
            is_selected = doll.id == selected_id
            card_class = "doll-card selected" if is_selected else "doll-card"
            with col:
                st.markdown(
                    f'<div class="{card_class}">'
                    f'<div class="doll-emoji">{doll.emoji}</div>'
                    f'<div class="doll-name">{doll.name}</div>'
                    f'<div class="doll-tagline">{doll.tagline}</div>'
                    f'<div style="color:#5C7A4A;font-weight:700;margin-top:0.5rem;">${doll.price:.0f}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if st.button(f"Select {doll.name}", key=f"pick_{doll.id}", use_container_width=True):
                    picked = doll.id

    return picked


def render_video(story, doll):
    video_path = get_video_path(story)
    if video_path:
        st.video(str(video_path))
    else:
        st.info("Video generating… this takes about 30–60 seconds on first run.")


def render_story(story, doll, generate_images: bool):
    st.markdown("---")
    st.markdown(f"## {story.title}")
    st.caption(
        f"~{story.reading_time_minutes} min · Starring **{story.child_name}** & **{story.doll_name}** · Apple Park"
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
        st.success(f"**Sweet dreams, {story.child_name}.** {story.moral}")


def render_cta(doll, child_name: str):
    st.markdown(
        f'<div class="cta-box">'
        f'<div class="cta-title">{child_name} loved this story?</div>'
        f'<div class="cta-text">Bring home <strong>{doll.name}</strong> — '
        f"100% GOTS organic cotton, hypoallergenic, and already friends with {child_name}.</div>"
        f'<div class="price-tag">${doll.price:.0f}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            f"🛒 Shop {doll.name} — ${doll.price:.0f}",
            doll.purchase_url,
            use_container_width=True,
            type="primary",
        )
        st.caption("Free shipping on orders $75+ · 30-day happiness guarantee")


def main():
    render_hero()

    characters = load_characters()

    if "selected_doll_id" not in st.session_state:
        st.session_state.selected_doll_id = characters[0].id
    if "story" not in st.session_state:
        st.session_state.story = None
    if "video_path" not in st.session_state:
        st.session_state.video_path = None

    col_input, col_doll = st.columns([1, 2])

    with col_input:
        st.markdown("#### Your child's name")
        child_name = st.text_input(
            "Child's first name",
            placeholder="e.g. Emma",
            label_visibility="collapsed",
        )
        child_age = st.number_input("Age (optional)", min_value=1, max_value=12, value=5, step=1)

        create_video = st.checkbox(
            "Create video story (narrated slideshow)",
            value=True,
            help="Generates an MP4 with voice narration and illustrated slides for each scene.",
        )

        generate_images = st.checkbox(
            "AI illustrations (requires OpenAI API key)",
            value=False,
            help="Uses DALL-E for custom scene art. Video stories use built-in illustrated slides.",
        )

        if os.getenv("OPENAI_API_KEY"):
            st.caption("✨ AI story generation available")
        else:
            st.caption("📖 Curated Apple Park stories (set OPENAI_API_KEY for unique AI stories)")

    with col_doll:
        st.session_state.selected_doll_id = render_doll_picker(
            characters, st.session_state.selected_doll_id
        )

    generate_clicked = st.button(
        "🎬 Create My Child's Video Story",
        type="primary",
        use_container_width=True,
        disabled=not child_name,
    )

    if not child_name:
        st.caption("Enter your child's name to unlock their personalized Apple Park story.")

    if generate_clicked:
        cleaned = sanitize_child_name(child_name)
        if not is_valid_child_name(cleaned):
            st.error("Please enter a valid first name (letters only, 2–32 characters).")
        else:
            doll = get_character(st.session_state.selected_doll_id)
            if doll is None:
                st.error("Please select an Apple Park Kids doll.")
            else:
                child = ChildProfile(name=cleaned, age=child_age)
                with st.spinner(f"Writing a story for {child.display_name()} and {doll.name}..."):
                    st.session_state.story = generate_story(child, doll)
                    st.session_state.video_path = None

                if create_video and st.session_state.story:
                    with st.spinner("Creating your video story — narrating scenes..."):
                        try:
                            video = generate_video_story(st.session_state.story, doll)
                            st.session_state.video_path = str(video)
                            st.session_state.story.video_path = str(video)
                        except Exception as exc:
                            st.warning(f"Video generation failed: {exc}. Story text is still available below.")

    if st.session_state.story:
        doll = get_character(st.session_state.story.doll_id)
        if doll:
            if st.session_state.video_path or st.session_state.story.video_path:
                st.markdown("### 🎬 Your Video Story")
                render_video(st.session_state.story, doll)

                video_file = st.session_state.video_path or st.session_state.story.video_path
                if video_file and os.path.exists(video_file):
                    with open(video_file, "rb") as handle:
                        st.download_button(
                            "Download video (MP4)",
                            handle.read(),
                            file_name=f"{st.session_state.story.child_name}-{doll.id}-apple-park-story.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                        )

            with st.expander("Read the full story text", expanded=not create_video):
                render_story(st.session_state.story, doll, generate_images)

            render_cta(doll, st.session_state.story.child_name)

            with st.expander("Share or save"):
                st.download_button(
                    "Download story as text",
                    st.session_state.story.full_text(),
                    file_name=f"{st.session_state.story.child_name}-{doll.id}-apple-park-story.txt",
                    mime="text/plain",
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
