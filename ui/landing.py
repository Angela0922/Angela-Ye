from __future__ import annotations

from pathlib import Path

from models.schemas import DollCharacter
from services.image_assets import brand_hero_path, doll_image_source

LANDING_CSS_PATH = Path(__file__).resolve().parent.parent / "landing" / "styles.css"


def load_landing_css() -> str:
    return LANDING_CSS_PATH.read_text(encoding="utf-8")


def render_landing_html(characters: list[DollCharacter]) -> str:
    hero_img = brand_hero_path()
    hero_src = str(hero_img) if hero_img else ""

    doll_cards = []
    for doll in characters:
        img = doll_image_source(doll) or doll.image_url
        trait = doll.personality[0].title() if doll.personality else ""
        tagline = doll.tagline[:72] + ("…" if len(doll.tagline) > 72 else "")
        doll_cards.append(
            f"""
            <article class="doll-card">
              <img src="{img}" alt="{doll.name} — Apple Park Kids doll" loading="lazy" />
              <div class="doll-body">
                <h3>{doll.name}</h3>
                <p>{trait} · {tagline}</p>
                <div class="doll-price">${doll.price:.0f}</div>
              </div>
            </article>
            """
        )

    hero_block = ""
    if hero_src:
        hero_block = f"""
          <div class="hero-visual">
            <div class="hero-card">
              <img src="{hero_src}" alt="Apple Park Kids organic cotton dolls" />
            </div>
            <div class="floating-badge">
              <strong>🌙 Bedtime stories that sell themselves</strong>
              <span>Name-aware tales starring your child &amp; their new best friend.</span>
            </div>
          </div>
        """

    return f"""
    <div class="landing-root">
      <section class="hero">
        <div class="container hero-grid">
          <div>
            <div class="pill">Free personalized preview</div>
            <h1>Your child's name.<br><em>Their perfect doll.</em><br>A story just for them.</h1>
            <p class="hero-lead">
              Tell us about your little one in a friendly chat. We'll match them with the right
              Apple Park Kids organic cotton doll, show you the product, and create a cozy bedtime
              story — before you buy.
            </p>
            <div class="hero-stats">
              <div class="stat"><strong>9</strong><span>doll friends</span></div>
              <div class="stat"><strong>Free</strong><span>story preview</span></div>
              <div class="stat"><strong>100%</strong><span>organic cotton</span></div>
            </div>
          </div>
          {hero_block}
        </div>
      </section>

      <section id="how-it-works">
        <div class="container">
          <div class="section-head">
            <h2>How it works</h2>
            <p>Three simple steps from chat to cozy bedtime magic.</p>
          </div>
          <div class="steps">
            <article class="step">
              <div class="step-num">1</div>
              <h3>Chat about your child</h3>
              <p>Share their name, age, favorite things, and personality. Our storyteller listens.</p>
            </article>
            <article class="step">
              <div class="step-num">2</div>
              <h3>Meet their match</h3>
              <p>We recommend the perfect Apple Park doll with photo, price, and shop link.</p>
            </article>
            <article class="step">
              <div class="step-num">3</div>
              <h3>Get their story</h3>
              <p>A personalized 3-scene bedtime tale — plus optional narrated video — starring them.</p>
            </article>
          </div>
        </div>
      </section>

      <section class="features">
        <div class="container">
          <div class="section-head">
            <h2>Why parents love it</h2>
            <p>Organic dolls meet thoughtful storytelling.</p>
          </div>
          <div class="feature-grid">
            <article class="feature">
              <h3>💬 Conversational matching</h3>
              <p>No forms to wrestle with — just tell us about your child like you would a friend.</p>
            </article>
            <article class="feature">
              <h3>🧸 Smart doll recommendations</h3>
              <p>Music lovers meet Gwen. Story lovers meet Wren. Every child gets a thoughtful match.</p>
            </article>
            <article class="feature">
              <h3>📖 Name-personalized stories</h3>
              <p>Your child's name woven through a gentle Apple Park adventure with their new doll friend.</p>
            </article>
            <article class="feature">
              <h3>🌿 Truly organic &amp; safe</h3>
              <p>GOTS-certified cotton, hypoallergenic fill, plastic-free — made for little ones.</p>
            </article>
          </div>
        </div>
      </section>

      <section id="dolls">
        <div class="container">
          <div class="section-head">
            <h2>Meet the Apple Park Kids</h2>
            <p>Nine inclusive organic cotton doll friends, each with their own personality.</p>
          </div>
          <div class="doll-grid">
            {"".join(doll_cards)}
          </div>
        </div>
      </section>

      <section>
        <div class="container">
          <div class="cta-band">
            <h2>Ready to find their perfect friend?</h2>
            <p>Start a free chat, get a doll match with product photo, and preview a bedtime story tonight.</p>
          </div>
        </div>
      </section>
    </div>
    """
