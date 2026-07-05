from __future__ import annotations

import os

import streamlit as st

from models.schemas import ChatMessage, ChatSession
from services.character_loader import get_character, load_characters
from services.chatbot import create_session, process_message
from services.illustrator import generate_scene_image, get_scene_image_path, scene_emoji, scene_gradient
from services.image_assets import brand_hero_path, doll_image_source
from services.story_generator import generate_story
from services.video_story import generate_video_story, get_video_path

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
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = create_session()
    if "video_path" not in st.session_state:
        st.session_state.video_path = None
    if "create_video" not in st.session_state:
        st.session_state.create_video = True


def render_hero():
    hero_img = brand_hero_path()
    col_text, col_img = st.columns([3, 2])
    with col_text:
        st.markdown(
            """
            <div class="hero-wrap" style="margin-bottom:0;">
                <div class="brand-pill">Apple Park Kids Story Chat</div>
                <div class="hero-title">
                    Tell us about your child,<br>
                    <em>we'll find their perfect doll &amp; story</em>
                </div>
                <p class="hero-subtitle">
                    Chat with our storyteller about your little one. We'll match them with the right
                    Apple Park Kids organic cotton doll, show you the product, and create a personalized
                    bedtime story — free before you buy.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_img:
        if hero_img:
            st.image(str(hero_img), use_container_width=True, caption="Apple Park Kids · Organic Cotton Dolls")


def render_trust_bar():
    st.markdown(
        """
        <div class="trust-bar">
            <span class="trust-item">💬 Chat-based personalization</span>
            <span class="trust-item">🧸 Smart doll matching</span>
            <span class="trust-item">📖 Free bedtime stories</span>
            <span class="trust-item">🌿 100% GOTS Organic Cotton</span>
        </div>
        """,
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


def render_story_results(session: ChatSession, generate_images: bool):
    story = session.story
    if not story:
        return

    doll = get_character(story.doll_id)
    if not doll:
        return

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
            st.markdown(f'<div class="scene-text">{scene.text}</div>', unsafe_allow_html=True)
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
    render_hero()
    render_trust_bar()

    session: ChatSession = st.session_state.chat_session

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
                st.session_state.chat_session = generate_story_for_session(session)
                st.rerun()

    if session.story:
        render_story_results(session, generate_images=st.session_state.get("generate_images", False))

    if prompt := st.chat_input("Tell me about your child…"):
        updated_session, _, _ = process_message(session, prompt)

        if updated_session.phase == "generating_story":
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
