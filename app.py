from __future__ import annotations

import os

import streamlit as st

from models.schemas import ChatMessage, ChatSession, ChildProfile, DollRecommendation
from services.character_loader import get_character, load_characters
from services.chatbot import create_session, process_message
from services.safety import is_valid_child_name, sanitize_child_name
from services.illustrator import generate_scene_image, get_scene_image_path, scene_emoji, scene_gradient
from services.image_assets import doll_image_source
from services.story_generator import generate_story, regenerate_story_for_child, swap_child_name_in_story
from services.video_story import generate_video_story
from ui.landing import load_landing_css

st.set_page_config(
    page_title="Apple Park Kids — Story Chat for Your Child",
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

    .chat-panel {
        background: #fff;
        border: 1px solid #E4DDD2;
        border-radius: 20px;
        padding: 1.25rem 1.25rem 0.5rem;
        margin-bottom: 1.5rem;
    }

    .product-card {
        background: #fff;
        border: 2px solid #5C7A4A;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    .product-title {
        font-family: 'Fraunces', serif;
        font-size: 1.4rem;
        color: #2E3D2E;
        margin-bottom: 0.5rem;
    }
    .product-reason {
        font-family: 'Nunito', sans-serif;
        color: #5A6B5A;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .price-tag {
        font-family: 'Fraunces', serif;
        font-size: 1.8rem;
        color: #5C7A4A;
        font-weight: 700;
    }

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

    .stButton > button[kind="primary"] {
        background: #5C7A4A !important;
        border-color: #5C7A4A !important;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
    }

    .landing-root section { padding: 2.5rem 0; }
    .landing-root .hero { padding-top: 1rem; }
    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .name-save-panel {
        background: #fff;
        border: 1px solid #E4DDD2;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .featuring-badge {
        display: inline-block;
        background: #EEF5EA;
        color: #5C7A4A;
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        font-size: 0.82rem;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        border: 1px solid #C5D9BC;
        margin-bottom: 1rem;
    }
    .story-box {
        background: #fff;
        border: 2px dashed #C5D9BC;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .story-box h3 {
        font-family: 'Fraunces', serif;
        color: #5C7A4A;
        margin: 0 0 1rem;
        font-size: 1.35rem;
    }
    .story-box p {
        font-family: 'Nunito', sans-serif;
        color: #3D4F3D;
        line-height: 1.75;
        margin: 0 0 1rem;
    }
    .chat-header-title {
        font-family: 'Fraunces', serif;
        font-size: 1.35rem;
        color: #2E3D2E;
        font-weight: 700;
    }
</style>
"""

LANDING_CSS = f"<style>{load_landing_css()}</style>"

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = create_session()
    if "video_path" not in st.session_state:
        st.session_state.video_path = None
    if "create_video" not in st.session_state:
        st.session_state.create_video = True
    if "view" not in st.session_state:
        st.session_state.view = "landing"
    if "selected_doll_id" not in st.session_state:
        st.session_state.selected_doll_id = "wren"
    if "landing_child_name" not in st.session_state:
        st.session_state.landing_child_name = ""
    if "chat_child_name" not in st.session_state:
        st.session_state.chat_child_name = ""

    query_name = st.query_params.get("name", "")
    if query_name and not st.session_state.landing_child_name:
        cleaned = _apply_child_name(query_name)
        if cleaned:
            st.session_state.landing_child_name = cleaned
            st.session_state.chat_child_name = cleaned
            st.session_state.chat_session = create_session(initial_name=cleaned)

    query_doll = st.query_params.get("doll", "")
    if query_doll and get_character(query_doll):
        st.session_state.selected_doll_id = query_doll


def _apply_child_name(name: str) -> str | None:
    cleaned = sanitize_child_name(name)
    if is_valid_child_name(cleaned):
        return cleaned
    return None


def _get_landing_child_name() -> str:
    return st.session_state.get("landing_child_name", "").strip()


def _highlight_child_name(text: str, child_name: str) -> str:
    if not child_name:
        return text
    import re

    return re.sub(
        re.compile(re.escape(child_name), re.IGNORECASE),
        lambda match: f"**{match.group(0)}**",
        text,
    )


def render_story_time_landing(characters):
    st.markdown(LANDING_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="nav" style="margin: -1rem -1rem 0; padding: 0 1rem;">
          <div class="container nav-inner">
            <div class="logo"><span>🍎</span> Apple Park Kids</div>
            <nav class="nav-links">
              <a href="https://appleparkkids.com" target="_blank">Shop</a>
            </nav>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="story-sky">
          <div class="pill">Welcome to the park!</div>
          <h1>Soft dolls. <em style="color:#5c7a4a;font-style:normal;">Sweet</em> stories.<br>Big imaginations.</h1>
          <p class="hero-lead">
            Meet the Apple Park Kids — organic cotton friends made for cuddles, tea parties,
            and sunny-day adventures. Enter your child's name in the ⭐ Your Child box and read
            a brand-new story starring them every time.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="park-friends-panel">
          <div class="section-head" style="margin-bottom:1.25rem;">
            <h2 style="margin:0;">Meet the Park Friends</h2>
            <p style="margin:0.35rem 0 0;">Nine lovable dolls — plus your little one can star in a story too!</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols_per_row = 4
    all_slots: list = list(characters) + [None]

    for row_start in range(0, len(all_slots), cols_per_row):
        row_items = all_slots[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, row_items):
            with col:
                if item is None:
                    st.markdown(
                        """
                        <div class="child-star-card">
                          <div class="child-star-icon">⭐</div>
                          <strong>Your Child</strong>
                          <small style="color:#5a6b5a;">Stars in the story!</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.text_input(
                        "Child's first name",
                        placeholder="Enter name here…",
                        label_visibility="collapsed",
                        key="landing_child_name",
                    )
                    preview = _apply_child_name(_get_landing_child_name())
                    if preview:
                        st.caption(f"✨ {preview} will appear in the story")
                else:
                    doll = item
                    img = doll_image_source(doll)
                    is_selected = doll.id == st.session_state.selected_doll_id
                    border = "2px dashed #e8c84a" if is_selected else "2px solid transparent"
                    st.markdown(f'<div class="doll-pick" style="border:{border};">', unsafe_allow_html=True)
                    if img:
                        st.image(str(img), use_container_width=True)
                    label = f"{'✓ ' if is_selected else ''}{doll.name}"
                    if st.button(label, key=f"pick_{doll.id}", use_container_width=True):
                        st.session_state.selected_doll_id = doll.id
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    child_name = _get_landing_child_name()
    cleaned_preview = _apply_child_name(child_name)
    selected = get_character(st.session_state.selected_doll_id)

    if cleaned_preview and selected:
        st.markdown(
            f'<div class="name-in-story-badge">📖 Your story will star <strong>{cleaned_preview}</strong> &amp; <strong>{selected.name}</strong></div>',
            unsafe_allow_html=True,
        )

    start_col, shop_col = st.columns([1, 1])
    with start_col:
        start_story = st.button(
            "⭐ Start Story Time",
            type="primary",
            use_container_width=True,
            disabled=not cleaned_preview,
        )
    with shop_col:
        st.link_button("Shop Dolls", "https://appleparkkids.com", use_container_width=True)

    if start_story:
        cleaned = _apply_child_name(_get_landing_child_name())
        if not cleaned:
            st.error("Please enter your child's name in the ⭐ Your Child box — it will appear in the story.")
            return

        doll = get_character(st.session_state.selected_doll_id)
        if not doll:
            st.error("Please pick an Apple Park friend.")
            return

        child = ChildProfile(name=cleaned)
        st.session_state.chat_session = create_session(initial_name=cleaned)
        st.session_state.chat_session.recommendation = DollRecommendation(
            doll_id=doll.id,
            doll_name=doll.name,
            reason=f"A cozy Apple Park adventure for {child.display_name()} and {doll.name}.",
        )
        st.session_state.chat_session.phase = "story_ready"

        with st.spinner(f"Writing a story starring {child.display_name()} & {doll.name}…"):
            story = generate_story(child, doll)
            st.session_state.chat_session.story = story
            st.session_state.video_path = None

            if story.full_text().lower().count(cleaned.lower()) < 2:
                st.error(f"We couldn't personalize the story for {cleaned}. Please try again.")
                return

            if st.session_state.create_video and story:
                try:
                    video = generate_video_story(story, doll)
                    st.session_state.video_path = str(video)
                    st.session_state.chat_session.story.video_path = str(video)
                except Exception as exc:
                    st.warning(f"Video failed: {exc}. Story text is still available below.")

        st.session_state.view = "story"
        st.rerun()

    if child_name and not cleaned_preview:
        st.warning("Use letters only for the name (2–32 characters) so it can appear in the story.")

    st.markdown("---")
    st.caption("Want help picking the perfect doll? Try our chat storyteller.")
    if st.button("💬 Chat for a personalized doll match"):
        cleaned = _apply_child_name(_get_landing_child_name())
        st.session_state.chat_session = create_session(initial_name=cleaned or "")
        st.session_state.view = "chat"
        st.rerun()

    st.markdown(
        """
        <div class="footer-bar">
            Wrapped in love, woven with purpose ·
            <a href="https://appleparkkids.com" target="_blank">appleparkkids.com</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_landing_page(characters):
    render_story_time_landing(characters)


def render_chat_header():
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("← Home"):
            st.session_state.view = "landing"
            st.rerun()
    with col_title:
        st.markdown(
            '<div class="chat-header-title">🍎 Story Chat — tell us about your child</div>',
            unsafe_allow_html=True,
        )


def render_story_header(child_name: str, doll_name: str):
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("← Back"):
            st.session_state.view = "landing"
            st.rerun()
    with col_title:
        st.markdown(
            f'<div class="chat-header-title">🌙 Story Time — {child_name} &amp; {doll_name}</div>',
            unsafe_allow_html=True,
        )


def render_product_match(session: ChatSession):
    if not session.recommendation:
        return

    doll = get_character(session.recommendation.doll_id)
    if not doll:
        return

    child_name = session.profile.display_name()
    img = doll_image_source(doll)

    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="product-title">Perfect match for {child_name}: {doll.name}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="product-reason">{session.recommendation.reason}</div>',
        unsafe_allow_html=True,
    )

    col_img, col_info = st.columns([1, 1])
    with col_img:
        if img:
            st.image(str(img), use_container_width=True, caption=f"{doll.name} — Apple Park Kids")
    with col_info:
        st.markdown(f"**{doll.tagline}**")
        st.markdown(f"**Themes:** {', '.join(doll.themes)}")
        st.markdown(f'<div class="price-tag">${doll.price:.0f}</div>', unsafe_allow_html=True)
        st.caption("100% GOTS organic cotton · hypoallergenic · plastic-free")
        st.link_button(
            f"Shop {doll.name} on AppleParkKids.com",
            doll.purchase_url,
            use_container_width=True,
            type="primary",
        )

    if session.recommendation.alternate_ids:
        st.markdown("**You might also love:**")
        alt_cols = st.columns(len(session.recommendation.alternate_ids))
        for col, alt_id in zip(alt_cols, session.recommendation.alternate_ids):
            alt_doll = get_character(alt_id)
            if not alt_doll:
                continue
            with col:
                alt_img = doll_image_source(alt_doll)
                if alt_img:
                    st.image(str(alt_img), use_container_width=True)
                st.caption(f"{alt_doll.name} · ${alt_doll.price:.0f}")
                st.link_button(f"View {alt_doll.name}", alt_doll.purchase_url, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_chat(session: ChatSession):
    st.markdown('<div class="chat-panel">', unsafe_allow_html=True)

    for message in session.messages:
        with st.chat_message("assistant" if message.role == "assistant" else "user"):
            st.markdown(message.content)

    st.markdown("</div>", unsafe_allow_html=True)


def render_name_save_bar(session: ChatSession) -> bool:
    """Name input + Save. Returns True if story was regenerated."""
    st.markdown('<div class="name-save-panel">', unsafe_allow_html=True)
    st.markdown("**Your child's name**")
    col_input, col_save = st.columns([4, 1])
    default_name = (session.story.child_name if session.story else session.profile.name) or _get_landing_child_name()
    if default_name and not st.session_state.get("story_save_name"):
        st.session_state.story_save_name = default_name
    with col_input:
        st.text_input(
            "Child name",
            placeholder="e.g. Angela",
            label_visibility="collapsed",
            key="story_save_name",
        )
    with col_save:
        save_clicked = st.button("Save", type="primary", use_container_width=True)
    st.caption("Saved names appear as the star of the story.")
    st.markdown("</div>", unsafe_allow_html=True)

    if not save_clicked:
        return False

    raw_name = st.session_state.get("story_save_name", "").strip()
    cleaned = _apply_child_name(raw_name)
    if not cleaned:
        st.error("Please enter a valid first name (letters only, 2–32 characters).")
        return False

    doll_id = session.story.doll_id if session.story else session.recommendation.doll_id if session.recommendation else st.session_state.selected_doll_id
    doll = get_character(doll_id)
    if not doll:
        st.error("Please pick an Apple Park friend first.")
        return False

    session.profile.name = cleaned
    st.session_state.landing_child_name = cleaned
    st.session_state.chat_child_name = cleaned

    with st.spinner(f"Updating story for {cleaned}…"):
        child = ChildProfile(name=cleaned, age=session.profile.age)
        session.story = regenerate_story_for_child(child, doll)
        session.profile = child
        if session.recommendation is None:
            session.recommendation = DollRecommendation(
                doll_id=doll.id,
                doll_name=doll.name,
                reason=f"A cozy Apple Park adventure for {cleaned} and {doll.name}.",
            )

    st.session_state.video_path = None
    if session.story.video_path:
        session.story.video_path = None
    st.success(f"Story updated — **{cleaned}** now stars in the tale!")
    return True


def render_story_results(session: ChatSession, generate_images: bool):
    story = session.story
    if not story:
        return

    doll = get_character(story.doll_id)
    if not doll:
        return

    if render_name_save_bar(session):
        st.session_state.chat_session = session
        st.rerun()

    st.markdown(
        f'<span class="featuring-badge">Featuring {story.child_name} &amp; {doll.name}</span>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="result-header">'
        f"<h2>🌙 {story.title}</h2>"
        f"<p>Starring <strong>{story.child_name}</strong> "
        f"&amp; <strong>{doll.name}</strong> · Apple Park</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    video_path = st.session_state.video_path or story.video_path
    if video_path and os.path.exists(video_path):
        st.video(str(video_path))
        with open(video_path, "rb") as handle:
            st.download_button(
                "⬇️ Download video (MP4)",
                handle.read(),
                file_name=f"{story.child_name}-{doll.id}-apple-park-story.mp4",
                mime="video/mp4",
                use_container_width=True,
            )

    with st.expander("📖 Read the full story", expanded=True):
        full_paragraphs = []
        for scene in story.scenes:
            full_paragraphs.append(scene.text)
        story_body = "\n\n".join(full_paragraphs)

        st.markdown('<div class="story-box">', unsafe_allow_html=True)
        st.markdown(f"### {story.title}")
        st.markdown(_highlight_child_name(story_body, story.child_name))
        st.markdown("</div>", unsafe_allow_html=True)

        for index, scene in enumerate(story.scenes):
            image_path = get_scene_image_path(story, scene, index)
            if generate_images and image_path is None:
                with st.spinner(f"Painting scene {index + 1}..."):
                    image_path = generate_scene_image(story, scene, doll, index)

            st.markdown('<div class="scene-card">', unsafe_allow_html=True)
            if image_path:
                st.image(str(image_path), caption=scene.illustration_caption, use_container_width=True)
            else:
                img = doll_image_source(doll)
                if img:
                    st.image(str(img), caption=scene.illustration_caption, use_container_width=True)
                else:
                    gradient = scene_gradient(doll, index)
                    emoji = scene_emoji(doll, index)
                    st.markdown(
                        f'<div style="background:{gradient};border-radius:12px;'
                        f'min-height:140px;display:flex;align-items:center;'
                        f'justify-content:center;font-size:3rem;">{emoji}</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown(f'<div class="scene-title">{scene.title}</div>', unsafe_allow_html=True)
            st.markdown(_highlight_child_name(scene.text, story.child_name))
            st.markdown("</div>", unsafe_allow_html=True)

        if story.moral:
            st.success(f"**Sweet dreams, {story.child_name}.** {story.moral}")

    render_product_match(session)


def generate_story_for_session(session: ChatSession) -> ChatSession:
    if not session.recommendation:
        return session

    doll = get_character(session.recommendation.doll_id)
    if not doll or not session.profile.has_name():
        return session

    with st.spinner(f"Writing {session.profile.display_name()} & {doll.name}'s story…"):
        session.story = generate_story(session.profile, doll)

    if st.session_state.create_video and session.story:
        with st.spinner("Creating narrated video — about a minute on first run…"):
            try:
                video = generate_video_story(session.story, doll)
                st.session_state.video_path = str(video)
                session.story.video_path = str(video)
            except Exception as exc:
                st.warning(f"Video failed: {exc}. Story text is still available below.")

    session.phase = "story_generated"
    return session


def main():
    init_session_state()
    characters = load_characters()

    if st.session_state.view == "landing":
        render_landing_page(characters)
        return

    session: ChatSession = st.session_state.chat_session

    if st.session_state.view == "story" and session.story:
        doll = get_character(session.story.doll_id)
        if doll:
            render_story_header(session.story.child_name, doll.name)
            render_story_results(session, generate_images=st.session_state.get("generate_images", False))
            st.markdown(
                """
                <div class="footer-bar">
                    Wrapped in love, woven with purpose ·
                    <a href="https://appleparkkids.com" target="_blank">appleparkkids.com</a>
                </div>
                """,
                unsafe_allow_html=True,
            )
        return

    render_chat_header()

    st.markdown("**Your child's first name** — appears in every scene of the story")
    st.text_input(
        "Child name",
        placeholder="e.g. Emma",
        label_visibility="collapsed",
        key="chat_child_name",
    )
    name_input = st.session_state.get("chat_child_name", "") or _get_landing_child_name()
    cleaned_name = _apply_child_name(name_input)
    if cleaned_name:
        session.profile.name = cleaned_name
        st.session_state.landing_child_name = cleaned_name
    elif name_input:
        st.warning("Please use letters only (2–32 characters) for the story name.")

    with st.expander("Options"):
        st.session_state.create_video = st.checkbox(
            "Create narrated video story (MP4)",
            value=st.session_state.create_video,
        )
        generate_images = st.checkbox(
            "AI illustrations (requires OpenAI API key)",
            value=False,
            key="generate_images",
        )
        if os.getenv("OPENAI_API_KEY"):
            st.caption("✨ AI chat, story generation, and doll matching enabled")
        else:
            st.caption("Using guided chat and curated story templates")

    render_chat(session)
    render_product_match(session)

    if session.phase in ("story_ready", "recommended", "story_generated") and session.recommendation:
        doll = get_character(session.recommendation.doll_id)
        if doll and not session.story:
            if st.button("🎬 Create My Child's Bedtime Story", type="primary", use_container_width=True):
                if not session.profile.has_name():
                    st.error("Please enter your child's name above — it will appear in the story.")
                else:
                    st.session_state.chat_session = generate_story_for_session(session)
                    st.session_state.view = "story"
                    st.rerun()

    if session.story:
        render_story_results(session, generate_images=st.session_state.get("generate_images", False))

    if prompt := st.chat_input("Tell me about your child…"):
        updated_session, _, _ = process_message(session, prompt)

        if updated_session.phase == "generating_story":
            if not updated_session.profile.has_name():
                updated_session.messages.append(
                    ChatMessage(
                        role="assistant",
                        content="I'd love to write the story — what's your child's first name? It will appear throughout the tale.",
                    )
                )
                updated_session.phase = "story_ready"
            else:
                updated_session = generate_story_for_session(updated_session)
                doll_name = (
                    updated_session.recommendation.doll_name
                    if updated_session.recommendation
                    else "their new friend"
                )
                updated_session.messages.append(
                    ChatMessage(
                        role="assistant",
                        content=(
                            f"Here's {updated_session.profile.display_name()}'s bedtime story! "
                            f"Scroll down to read it, watch the video, and meet {doll_name}."
                        ),
                    )
                )
                st.session_state.view = "story"

        st.session_state.chat_session = updated_session
        st.rerun()

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


if __name__ == "__main__":
    main()
