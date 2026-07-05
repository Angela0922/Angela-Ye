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
    page_title="Apple Park Kids — A Bedtime Story Just for Your Child",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;500;700&family=Nunito:wght@400;600;700&display=swap');

    .stApp {
        background: #FAF7F2;
    }

    .block-container {
        padding-top: 1.5rem;
        max-width: 1100px;
    }

    /* ── Hero ── */
    .hero-wrap {
        background: linear-gradient(135deg, #EAF2E6 0%, #F5F0E8 50%, #EDE8DF 100%);
        border-radius: 24px;
        padding: 2.5rem 2.5rem 2rem;
        margin-bottom: 2rem;
        border: 1px solid #D8E4D0;
        position: relative;
        overflow: hidden;
    }
    .hero-wrap::before {
        content: "🍎";
        position: absolute;
        right: 2rem;
        top: 1.5rem;
        font-size: 4rem;
        opacity: 0.12;
    }
    .brand-pill {
        display: inline-block;
        background: #fff;
        color: #5C7A4A;
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        border: 1px solid #C5D9BC;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
    .hero-title {
        font-family: 'Fraunces', serif;
        font-size: clamp(1.9rem, 4vw, 2.8rem);
        font-weight: 700;
        color: #2E3D2E;
        line-height: 1.12;
        margin: 0 0 0.75rem 0;
    }
    .hero-title em {
        font-style: normal;
        color: #5C7A4A;
    }
    .hero-subtitle {
        font-family: 'Nunito', sans-serif;
        font-size: 1.05rem;
        color: #5A6B5A;
        line-height: 1.65;
        max-width: 620px;
        margin: 0;
    }
    .hero-quote {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 0.95rem;
        color: #7A8F72;
        margin-top: 1.2rem;
        padding-top: 1rem;
        border-top: 1px solid #D8E4D0;
    }

    /* ── Trust bar ── */
    .trust-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin: 1.5rem 0 2rem;
    }
    .trust-item {
        background: #fff;
        border: 1px solid #E4DDD2;
        border-radius: 10px;
        padding: 0.45rem 0.9rem;
        font-family: 'Nunito', sans-serif;
        font-size: 0.82rem;
        color: #4A5A4A;
        font-weight: 600;
    }

    /* ── Steps ── */
    .steps-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    @media (max-width: 700px) {
        .steps-row { grid-template-columns: 1fr; }
    }
    .step-card {
        background: #fff;
        border: 1px solid #E4DDD2;
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
    }
    .step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px; height: 28px;
        background: #5C7A4A;
        color: #fff;
        border-radius: 50%;
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    .step-title {
        font-family: 'Fraunces', serif;
        font-size: 1rem;
        color: #2E3D2E;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .step-desc {
        font-family: 'Nunito', sans-serif;
        font-size: 0.82rem;
        color: #6B7B6B;
        line-height: 1.45;
    }

    /* ── Form panel ── */
    .form-panel {
        background: #fff;
        border: 1px solid #E4DDD2;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .section-label {
        font-family: 'Fraunces', serif;
        font-size: 1.25rem;
        color: #2E3D2E;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .section-hint {
        font-family: 'Nunito', sans-serif;
        font-size: 0.85rem;
        color: #7A8A7A;
        margin-bottom: 1rem;
    }

    /* ── Doll cards ── */
    .doll-card {
        background: #FAF7F2;
        border: 2px solid #E4DDD2;
        border-radius: 14px;
        padding: 0.85rem 0.6rem;
        text-align: center;
        min-height: 155px;
        transition: border-color 0.15s;
    }
    .doll-card.selected {
        border-color: #5C7A4A;
        background: #EEF5EA;
        box-shadow: 0 0 0 3px rgba(92,122,74,0.12);
    }
    .doll-emoji { font-size: 2.2rem; line-height: 1; margin-bottom: 0.25rem; }
    .doll-name {
        font-family: 'Fraunces', serif;
        font-size: 1rem;
        color: #2E3D2E;
        font-weight: 700;
    }
    .doll-trait {
        font-family: 'Nunito', sans-serif;
        font-size: 0.7rem;
        color: #7A8A7A;
        margin-top: 0.2rem;
        line-height: 1.3;
    }
    .doll-price {
        font-family: 'Nunito', sans-serif;
        font-size: 0.8rem;
        color: #5C7A4A;
        font-weight: 700;
        margin-top: 0.35rem;
    }

    /* ── Results ── */
    .result-header {
        background: linear-gradient(135deg, #5C7A4A, #7D9B76);
        color: #fff;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin: 2rem 0 1.5rem;
        text-align: center;
    }
    .result-header h2 {
        font-family: 'Fraunces', serif;
        font-size: 1.6rem;
        margin: 0 0 0.3rem;
        color: #fff;
    }
    .result-header p {
        font-family: 'Nunito', sans-serif;
        font-size: 0.95rem;
        margin: 0;
        opacity: 0.9;
    }

    .scene-card {
        background: #fff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #E4DDD2;
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
        font-size: 1.2rem;
        color: #5C7A4A;
        margin-bottom: 0.4rem;
    }
    .scene-text {
        font-family: 'Nunito', sans-serif;
        font-size: 1rem;
        color: #3D4F3D;
        line-height: 1.7;
    }

    .cta-box {
        background: #fff;
        border: 2px solid #5C7A4A;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin-top: 1.5rem;
    }
    .cta-title {
        font-family: 'Fraunces', serif;
        font-size: 1.5rem;
        color: #2E3D2E;
    }
    .cta-text {
        font-family: 'Nunito', sans-serif;
        color: #5A6B5A;
        font-size: 0.95rem;
        line-height: 1.55;
        margin: 0.5rem 0 1rem;
    }
    .price-tag {
        font-family: 'Fraunces', serif;
        font-size: 2rem;
        color: #5C7A4A;
        font-weight: 700;
    }
    .organic-note {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem;
        color: #8A9A82;
        margin-top: 0.5rem;
    }

    .footer-bar {
        text-align: center;
        padding: 2rem 0 1rem;
        font-family: 'Nunito', sans-serif;
        font-size: 0.82rem;
        color: #9AAA92;
        border-top: 1px solid #E4DDD2;
        margin-top: 3rem;
    }
    .footer-bar a { color: #5C7A4A; text-decoration: none; font-weight: 600; }

    div[data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Streamlit button polish */
    .stButton > button[kind="primary"] {
        background: #5C7A4A !important;
        border-color: #5C7A4A !important;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #4A6340 !important;
        border-color: #4A6340 !important;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero():
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="brand-pill">Apple Park Kids</div>
            <div class="hero-title">
                A bedtime video story starring<br>
                <em>your child</em> &amp; their new best friend
            </div>
            <p class="hero-subtitle">
                Type your little one's name, pick an organic cotton doll, and watch a
                personalized narrated story come to life — free, before you buy.
                Every Apple Park Kid has their own adventure waiting in the park.
            </p>
            <p class="hero-quote">
                "A perfect day in Apple Park has already begun."
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trust_bar():
    st.markdown(
        """
        <div class="trust-bar">
            <span class="trust-item">🌿 100% GOTS Organic Cotton</span>
            <span class="trust-item">🚫 Plastic-Free &amp; Hypoallergenic</span>
            <span class="trust-item">🎬 Free Personalized Video Preview</span>
            <span class="trust-item">🧸 9 Inclusive Doll Characters</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_how_it_works():
    st.markdown(
        """
        <div class="steps-row">
            <div class="step-card">
                <div class="step-num">1</div>
                <div class="step-title">Say their name</div>
                <div class="step-desc">Enter your child's first name — it appears throughout the story and narration.</div>
            </div>
            <div class="step-card">
                <div class="step-num">2</div>
                <div class="step-title">Pick a doll</div>
                <div class="step-desc">Choose from Alex, Ella, Grady, Gwen, Levi, Luke, Mia, Paloma, or Wren.</div>
            </div>
            <div class="step-card">
                <div class="step-num">3</div>
                <div class="step-title">Watch the magic</div>
                <div class="step-desc">A narrated video bedtime story plays — starring your child and their new friend.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_doll_picker(characters: list, selected_id: str | None) -> str | None:
    st.markdown('<div class="section-label">Meet the Apple Park Kids</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-hint">Each doll has a unique personality and their own bedtime story.</div>',
        unsafe_allow_html=True,
    )

    picked = selected_id
    cols_per_row = 3

    for row_start in range(0, len(characters), cols_per_row):
        row_chars = characters[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, doll in zip(cols, row_chars):
            is_selected = doll.id == selected_id
            card_class = "doll-card selected" if is_selected else "doll-card"
            trait = doll.personality[0].title() if doll.personality else ""
            with col:
                st.markdown(
                    f'<div class="{card_class}">'
                    f'<div class="doll-emoji">{doll.emoji}</div>'
                    f'<div class="doll-name">{doll.name}</div>'
                    f'<div class="doll-trait">{trait}</div>'
                    f'<div class="doll-price">${doll.price:.0f}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                label = f"{'✓ ' if is_selected else ''}Choose {doll.name}"
                if st.button(label, key=f"pick_{doll.id}", use_container_width=True):
                    picked = doll.id

    return picked


def render_video(story):
    video_path = get_video_path(story)
    if video_path:
        st.video(str(video_path))
    else:
        st.info("Video generating… this takes about 30–60 seconds on first run.")


def render_story(story, doll, generate_images: bool):
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
        f'<div class="cta-title">{child_name} &amp; {doll.name} — best friends already?</div>'
        f'<div class="cta-text">'
        f"Bring home <strong>{doll.name}</strong> tonight. Handcrafted from 100% GOTS organic cotton "
        f"with naturally hypoallergenic corn fiber fill — the doll who already knows {child_name}'s name."
        f"</div>"
        f'<div class="price-tag">${doll.price:.0f}</div>'
        f'<div class="organic-note">Free shipping on orders $75+ · 30-day happiness guarantee</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            f"Shop {doll.name} on AppleParkKids.com",
            doll.purchase_url,
            use_container_width=True,
            type="primary",
        )


def render_footer():
    st.markdown(
        """
        <div class="footer-bar">
            Wrapped in love, woven with purpose ·
            <a href="https://appleparkkids.com" target="_blank">appleparkkids.com</a>
            · Organic cotton dolls &amp; toys for little ones
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    render_hero()
    render_trust_bar()
    render_how_it_works()

    characters = load_characters()

    if "selected_doll_id" not in st.session_state:
        st.session_state.selected_doll_id = characters[0].id
    if "story" not in st.session_state:
        st.session_state.story = None
    if "video_path" not in st.session_state:
        st.session_state.video_path = None

    st.markdown('<div class="form-panel">', unsafe_allow_html=True)

    col_name, col_age = st.columns([2, 1])
    with col_name:
        st.markdown('<div class="section-label">Your child\'s first name</div>', unsafe_allow_html=True)
        child_name = st.text_input(
            "Child's first name",
            placeholder="e.g. Emma, Noah, Sofia…",
            label_visibility="collapsed",
        )
    with col_age:
        st.markdown('<div class="section-label">Age</div>', unsafe_allow_html=True)
        child_age = st.number_input("Age", min_value=1, max_value=12, value=5, step=1, label_visibility="collapsed")

    st.session_state.selected_doll_id = render_doll_picker(characters, st.session_state.selected_doll_id)

    selected_doll = get_character(st.session_state.selected_doll_id)
    if selected_doll and child_name:
        cleaned_preview = sanitize_child_name(child_name)
        if is_valid_child_name(cleaned_preview):
            preview_name = cleaned_preview[:1].upper() + cleaned_preview[1:]
            st.markdown(
                f'<div class="section-hint" style="text-align:center;margin-top:0.5rem;">'
                f"Ready to create: <strong>{preview_name}</strong> &amp; <strong>{selected_doll.name}</strong>"
                f"'s Apple Park adventure</div>",
                unsafe_allow_html=True,
            )

    create_video = True
    generate_images = False

    with st.expander("Advanced options"):
        create_video = st.checkbox(
            "Create narrated video story (MP4)",
            value=True,
            help="Generates a voice-narrated video with illustrated slides.",
        )
        generate_images = st.checkbox(
            "AI illustrations for text view (requires OpenAI API key)",
            value=False,
        )
        if os.getenv("OPENAI_API_KEY"):
            st.caption("✨ AI story generation enabled")
        else:
            st.caption("Using curated Apple Park story templates")

    st.markdown("</div>", unsafe_allow_html=True)

    generate_clicked = st.button(
        "🎬  Create My Child's Bedtime Video Story",
        type="primary",
        use_container_width=True,
        disabled=not child_name,
    )

    if not child_name:
        st.caption("↑ Enter your child's name above to get started — it's free!")

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
                with st.spinner(f"Writing {child.display_name()} & {doll.name}'s story…"):
                    st.session_state.story = generate_story(child, doll)
                    st.session_state.video_path = None

                if create_video and st.session_state.story:
                    with st.spinner("Creating your narrated video — this takes about a minute…"):
                        try:
                            video = generate_video_story(st.session_state.story, doll)
                            st.session_state.video_path = str(video)
                            st.session_state.story.video_path = str(video)
                        except Exception as exc:
                            st.warning(f"Video failed: {exc}. Story text is still available below.")

    if st.session_state.story:
        doll = get_character(st.session_state.story.doll_id)
        if doll:
            st.markdown(
                f'<div class="result-header">'
                f"<h2>🌙 {st.session_state.story.title}</h2>"
                f"<p>Starring <strong>{st.session_state.story.child_name}</strong> "
                f"&amp; <strong>{doll.name}</strong> · Apple Park</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

            if st.session_state.video_path or st.session_state.story.video_path:
                render_video(st.session_state.story)

                video_file = st.session_state.video_path or st.session_state.story.video_path
                if video_file and os.path.exists(video_file):
                    with open(video_file, "rb") as handle:
                        st.download_button(
                            "⬇️ Download video (MP4)",
                            handle.read(),
                            file_name=f"{st.session_state.story.child_name}-{doll.id}-apple-park-story.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                        )

            with st.expander("📖 Read the full story", expanded=False):
                render_story(st.session_state.story, doll, generate_images)

            render_cta(doll, st.session_state.story.child_name)

    render_footer()


if __name__ == "__main__":
    main()
