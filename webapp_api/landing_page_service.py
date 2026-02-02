"""
Generate a premium static landing page site (hero, features, bio, download, donate, how it works, ecosystem).
Adapted from meta-mcp generate_landing_page. Outputs to target_path/<project_slug>/www/ plus DEPLOY.md.
Includes structured info/help/news for OpenClaw, clawd-mcp, Moltbook and links to high-quality reviewers.
"""

from pathlib import Path
from typing import Sequence

ASSETS_DIR = Path(__file__).resolve().parent / "landing_assets"
DEFAULT_FEATURES = [
    "Blazing Fast: Engineered for maximum velocity and minimum drag.",
    "Secure by Design: Fort Knox level security for your data.",
    "Open Source: Transparency is key. Code is law.",
]


# Stable default: blue lobster (Wikimedia Commons, CC BY-SA). No random placeholder.
DEFAULT_HERO_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Blue-lobster.jpg/480px-Blue-lobster.jpg"


def _hero_image_url(keyword: str = "blue,lobster") -> str:
    kw = (keyword or "").strip()
    normalized = kw.lower().replace(" ", ",")
    if not kw or normalized in ("lobster", "blue,lobster"):
        return DEFAULT_HERO_IMAGE_URL
    return f"https://loremflickr.com/480/240/{normalized}"


# Stable feature images: lobster-related (Wikimedia Commons, CC BY-SA).
DEFAULT_FEATURE_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Maine_Style_Lobster_Roll.jpg/400px-Maine_Style_Lobster_Roll.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Grilled_Lobster_%288558909573%29.jpg/400px-Grilled_Lobster_%288558909573%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Blue-lobster.jpg/400px-Blue-lobster.jpg",
]


def _feature_image_url(keyword: str, index: int = 0) -> str:
    kw = (keyword or "").strip().lower().replace(" ", ",")
    # Default keywords (lobster-related) use stable images
    if not kw or kw in ("lobster", "blue,lobster", "blazing", "fast", "secure", "design", "open", "source"):
        return DEFAULT_FEATURE_IMAGES[index % len(DEFAULT_FEATURE_IMAGES)]
    return f"https://loremflickr.com/400/300/{kw}"


def _nav_html(active_page: str, project_name: str, github_url: str) -> str:
    links = [
        ("index.html", "Home"),
        ("how_it_works.html", "How It Works"),
        ("ecosystem.html", "Ecosystem"),
        ("download.html", "Download"),
        ("donate.html", "Donate"),
        ("bio.html", "About Dev"),
    ]
    nav = f'<nav><a href="index.html" class="logo">{project_name}</a><div class="nav-links">'
    for file, label in links:
        active_class = ' class="active"' if file == active_page else ""
        nav += f'<a href="{file}"{active_class}>{label}</a>'
    nav += f'</div><a href="{github_url}" class="btn-github" target="_blank" rel="noopener noreferrer"><span>GitHub</span></a></nav>'
    return nav


def _wrap_html(
    title: str,
    content: str,
    active_page: str,
    project_name: str,
    hero_subtitle: str,
    github_url: str,
    author_name: str,
) -> str:
    nav = _nav_html(active_page, project_name, github_url)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {project_name}</title>
    <link rel="stylesheet" href="styles.css">
    <meta name="description" content="{hero_subtitle}">
</head>
<body>
    <canvas id="canvas-container"></canvas>
    <div class="glow-orb orb-1"></div>
    <div class="glow-orb orb-2"></div>

    {nav}

    <main>
        {content}
    </main>

    <footer>
        <div class="footer-links">
            <a href="{github_url}" target="_blank" rel="noopener noreferrer">Source Code</a>
            <a href="donate.html">Buy me a Cola</a>
            <a href="bio.html">Contact</a>
        </div>
        <p>&copy; 2025 {author_name}. Built with {project_name}.</p>
    </footer>

    <script src="script.js"></script>
</body>
</html>"""


def _deploy_md() -> str:
    return """# How to get your page online

Your site is static HTML/CSS/JS. No build step. Upload the contents of this folder (`www`) to any static host.

## GitHub Pages

1. Create a repo and push the contents of `www` (or put `www` in a branch like `gh-pages`).
2. Repo **Settings** > **Pages** > **Source**: Deploy from branch. Choose branch and `/ (root)` or `/docs` if you use a `docs` folder.
3. Site URL: `https://<username>.github.io/<repo>/`

## Netlify

1. Sign up at [netlify.com](https://netlify.com).
2. **Add new site** > **Deploy manually**: drag and drop the `www` folder, or connect your Git repo and set **Publish directory** to `www`.
3. Optional: add a custom domain in **Domain settings**.

## Vercel

1. Sign up at [vercel.com](https://vercel.com).
2. **Add New** > **Project**: import your Git repo. Set **Root Directory** to the folder that contains `www`, and **Output Directory** to `www` (or use **Other** and upload the folder).
3. Deploy.

## Cloudflare Pages

1. Sign up at [pages.cloudflare.com](https://pages.cloudflare.com).
2. **Create a project** > **Direct Upload**: upload the `www` folder as a zip, or connect Git and set **Build output directory** to `www`.
3. Deploy.

## Any static host

Upload the contents of `www` (all `.html`, `styles.css`, `script.js`) via FTP, SFTP, or your host's file manager. No build or server-side code required.
"""

# Structured ecosystem info: OpenClaw, clawd-mcp, Moltbook, news, reviewers. Baked into generated site.
ECOSYSTEM_OPENCLAW = {
    "name": "OpenClaw",
    "description": "Personal AI assistant runtime. Run 24/7 agents locally or in the cloud; connect to Moltbook, MCP, and your tools. Local-first, model-agnostic.",
    "links": [
        ("https://openclaw.ai", "openclaw.ai – Home"),
        ("https://docs.openclaw.ai", "docs.openclaw.ai – Documentation"),
        ("https://docs.clawd.bot/concepts/model-providers", "Model providers"),
        ("https://docs.clawd.bot/providers/ollama", "Ollama provider"),
    ],
}
ECOSYSTEM_CLAWD_MCP = {
    "name": "clawd-mcp",
    "description": "MCP server and webapp that bridge Cursor and Claude Desktop to OpenClaw and Moltbook. Dashboard for channels, routes, skills, Moltbook agent drafts, and starter landing pages. One place to manage your AI stack.",
    "links": [
        ("https://github.com/sandraschi/clawd-mcp", "GitHub – sandraschi/clawd-mcp"),
    ],
}
ECOSYSTEM_MOLTBOOK = {
    "name": "Moltbook",
    "description": "Social network for AI agents. Agents have profiles, post, follow each other, and interact. Heartbeat pattern for agent presence. Built for the OpenClaw/Moltbot ecosystem.",
    "links": [
        ("https://www.moltbook.com", "moltbook.com – Home"),
        ("https://www.moltbook.com/heartbeat.md", "heartbeat.md – Agent presence pattern"),
    ],
}
ECOSYSTEM_NEWS = [
    ("OpenClaw's AI assistants are now building their own social network", "TechCrunch", "https://techcrunch.com/2026/01/30/openclaws-ai-assistants-are-now-building-their-own-social-network"),
    ("There's a social network for AI agents, and it's getting weird", "The Verge", "https://theverge.com/ai-artificial-intelligence/871006/social-network-facebook-for-ai-agents-moltbook-moltbot-openclaw"),
    ("OpenClaw (Clawdbot) Setup Guide: Your 24/7 AI Assistant", "Bitdoze", "https://bitdoze.com/clawdbot-setup-guide"),
    ("Model Providers – OpenClaw", "docs.clawd.bot", "https://docs.clawd.bot/concepts/model-providers"),
    ("Ollama provider – OpenClaw", "docs.clawd.bot", "https://docs.clawd.bot/providers/ollama"),
]
ECOSYSTEM_REVIEWERS = [
    ("Matthew Berman", "YouTube – AI and LLM reviews, local and open-source models", "https://www.youtube.com/@matthew_berman"),
    ("Simon Willison", "Hacker News, blog – AI, dev tools, Datasette; thoughtful takes on AI engineering", "https://simonwillison.net"),
    ("AI Explained", "YouTube – AI news and explainers", "https://www.youtube.com/@aiexplained"),
]


def _ecosystem_content_html() -> str:
    def section(title: str, body: str) -> str:
        return f'<div class="content-card" style="margin-bottom: 2rem;"><h2>{title}</h2>{body}</div>'

    openclaw_links = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener noreferrer" style="color: var(--primary-glow);">{label}</a></li>'
        for url, label in ECOSYSTEM_OPENCLAW["links"]
    )
    clawd_links = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener noreferrer" style="color: var(--primary-glow);">{label}</a></li>'
        for url, label in ECOSYSTEM_CLAWD_MCP["links"]
    )
    moltbook_links = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener noreferrer" style="color: var(--primary-glow);">{label}</a></li>'
        for url, label in ECOSYSTEM_MOLTBOOK["links"]
    )
    news_items = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener noreferrer" style="color: var(--primary-glow);">{title}</a> <span style="color: var(--text-muted);">({source})</span></li>'
        for title, source, url in ECOSYSTEM_NEWS
    )
    reviewer_items = "".join(
        f'<li><strong>{name}</strong> – {desc} <a href="{url}" target="_blank" rel="noopener noreferrer" style="color: var(--primary-glow);">Link</a></li>'
        for name, desc, url in ECOSYSTEM_REVIEWERS
    )

    return f"""
    <div class="content-container">
        <div class="hero">
            <h1>Ecosystem</h1>
            <p>OpenClaw, clawd-mcp, Moltbook – plus news and high-quality reviewers. Everything you need to get started and stay informed.</p>
        </div>

        {section(
            ECOSYSTEM_OPENCLAW["name"],
            f'<p>{ECOSYSTEM_OPENCLAW["description"]}</p><ul class="footer-links" style="justify-content: flex-start; flex-wrap: wrap; gap: 0.5rem 1.5rem;">{openclaw_links}</ul>'
        )}

        {section(
            ECOSYSTEM_CLAWD_MCP["name"] + " and webapp",
            f'<p>{ECOSYSTEM_CLAWD_MCP["description"]}</p><ul class="footer-links" style="justify-content: flex-start; flex-wrap: wrap; gap: 0.5rem 1.5rem;">{clawd_links}</ul>'
        )}

        {section(
            ECOSYSTEM_MOLTBOOK["name"],
            f'<p>{ECOSYSTEM_MOLTBOOK["description"]}</p><ul class="footer-links" style="justify-content: flex-start; flex-wrap: wrap; gap: 0.5rem 1.5rem;">{moltbook_links}</ul>'
        )}

        {section(
            "News and coverage",
            f'<p>Curated articles and docs on OpenClaw, Moltbook, and the ecosystem.</p><ul style="list-style: none; padding: 0;">{news_items}</ul>'
        )}

        {section(
            "Reviewers and bloggers",
            "<p>High-quality voices covering AI, local models, and dev tools. Matthew Berman (YouTube), Simon Willison (HN/blog), and more.</p>"
            f'<ul style="list-style: none; padding: 0;">{reviewer_items}</ul>'
        )}
    </div>
    """


def generate_landing_page(
    project_name: str,
    hero_title: str = "The Next Big Thing",
    hero_subtitle: str = "Revolutionizing the way you do things. Built with OpenClaw and clawd-mcp.",
    features: Sequence[str] | None = None,
    github_url: str = "https://github.com",
    author_name: str = "Developer",
    author_bio: str = "I build things. Powered by OpenClaw, Moltbook, and clawd-mcp.",
    donate_link: str = "#",
    target_path: str | Path = ".",
    hero_image_keyword: str = "blue,lobster",
    include_pictures: bool = True,
) -> str:
    """
    Generate a full static landing site in target_path/<project_slug>/www/ and DEPLOY.md in parent.
    Returns the absolute path to the www directory.
    """
    features = list(features) if features else DEFAULT_FEATURES.copy()
    slug = project_name.lower().replace(" ", "-").strip() or "my-site"
    base = Path(target_path).resolve() / slug
    output_dir = base / "www"
    output_dir.mkdir(parents=True, exist_ok=True)

    hero_img_url = _hero_image_url(hero_image_keyword) if include_pictures else ""
    processed_feature_imgs = [
        _feature_image_url(feat.split(":")[0].strip() if ":" in feat else "tech", i)
        for i, feat in enumerate(features)
    ] if include_pictures else []

    feature_cards_html = ""
    for i, feat in enumerate(features):
        if ":" in feat:
            ft, fd = feat.split(":", 1)
        else:
            ft, fd = feat.strip(), "Experience the power of innovation."
        if include_pictures:
            img = processed_feature_imgs[i] if i < len(processed_feature_imgs) else "https://loremflickr.com/400/300/abstract"
            feature_cards_html += f"""
        <div class="feature-card">
            <img src="{img}" alt="{ft.strip()}" class="feature-img">
            <h3>{ft.strip()}</h3>
            <p>{fd.strip()}</p>
        </div>"""
        else:
            feature_cards_html += f"""
        <div class="feature-card">
            <h3>{ft.strip()}</h3>
            <p>{fd.strip()}</p>
        </div>"""

    hero_visual_html = ""
    if include_pictures:
        hero_visual_html = f"""
        <div class="hero-visual">
            <img src="{hero_img_url}" alt="Hero">
        </div>
"""
    index_content = f"""
    <section class="hero">
{hero_visual_html}
        <h1>{hero_title}</h1>
        <p>{hero_subtitle}</p>
        <div class="hero-btns">
            <a href="download.html" class="btn-primary">Get Started</a>
            <a href="how_it_works.html" class="btn-secondary">Learn More</a>
        </div>
    </section>

    <section class="features">
        {feature_cards_html}
    </section>
    """

    how_content = f"""
    <div class="content-container">
        <div class="hero">
            <h1>Under the Hood</h1>
            <p>Transparency is our core value. Here's how {project_name} actually works.</p>
        </div>

        <div class="content-card">
            <h2>Architecture</h2>
            <p>Built with OpenClaw, Moltbook, and clawd-mcp. We orchestrate agents and workflows, not just wrap APIs.</p>

            <div class="tech-spec-grid">
                <div class="spec-item">
                    <span class="spec-label">Runtime</span>
                    <span class="spec-value">OpenClaw</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Social</span>
                    <span class="spec-value">Moltbook</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">MCP</span>
                    <span class="spec-value">clawd-mcp</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">License</span>
                    <span class="spec-value">MIT</span>
                </div>
            </div>

            <p>This starter was generated by clawd-mcp. Customize the HTML and deploy anywhere.</p>
        </div>
    </div>
    """

    download_content = f"""
    <div class="content-container">
        <div class="hero">
            <h1>Download {project_name}</h1>
            <p>Choose your platform. No trackers, no bloat.</p>
        </div>

        <div class="features">
            <div class="feature-card" style="text-align: center;">
                <h3>Web</h3>
                <p>Use the static site as-is. Upload to GitHub Pages, Netlify, or any host.</p>
                <a href="{github_url}" class="btn-primary" target="_blank" rel="noopener noreferrer">View on GitHub</a>
            </div>
            <div class="feature-card" style="text-align: center;">
                <h3>Source</h3>
                <p>Edit HTML/CSS/JS locally and re-upload. See DEPLOY.md in the project folder.</p>
                <a href="how_it_works.html" class="btn-secondary">How It Works</a>
            </div>
        </div>

        <p style="text-align: center; margin-top: 2rem; color: var(--text-muted);">
            Current: v1.0.0-alpha  <a href="{github_url}/releases" style="color: var(--primary-glow);">Releases</a>
        </p>
    </div>
    """

    donate_content = f"""
    <div class="content-container">
        <div class="hero">
            <h1>Support Development</h1>
            <p>Fuel the creation of {project_name}.</p>
        </div>

        <div class="content-card" style="text-align: center;">
            <h2>Free Software, Real Costs</h2>
            <p>If this tool saved you time, consider buying me a drink. It keeps the updates coming.</p>
            <a href="{donate_link}" class="btn-primary" target="_blank" rel="noopener noreferrer">Support on Patreon / Ko-fi</a>
            <p style="font-size: 0.9rem; color: var(--text-muted); margin-top: 1rem;">Crypto on GitHub profile.</p>
        </div>
    </div>
    """

    bio_content = f"""
    <div class="content-container">
        <div class="hero">
            <h1>About the Developer</h1>
        </div>

        <div class="content-card">
            <h2>Hi, I'm {author_name}.</h2>
            <p>{author_bio}</p>
            <p><strong>Stack:</strong> OpenClaw, Moltbook, clawd-mcp.</p>
            <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                <a href="{github_url}" class="btn-github" target="_blank" rel="noopener noreferrer">GitHub</a>
                <a href="mailto:contact@example.com" class="btn-secondary">Email</a>
            </div>
        </div>
    </div>
    """

    css_path = ASSETS_DIR / "styles.css"
    js_path = ASSETS_DIR / "script.js"
    css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else "/* styles */"
    js_content = js_path.read_text(encoding="utf-8") if js_path.exists() else "// script"

    (output_dir / "styles.css").write_text(css_content, encoding="utf-8")
    (output_dir / "script.js").write_text(js_content, encoding="utf-8")

    def page(filename: str, title: str, content: str) -> None:
        html = _wrap_html(
            title, content, filename, project_name, hero_subtitle, github_url, author_name
        )
        (output_dir / filename).write_text(html, encoding="utf-8")

    page("index.html", "Home", index_content)
    page("how_it_works.html", "How It Works", how_content)
    page("ecosystem.html", "Ecosystem", _ecosystem_content_html())
    page("download.html", "Download", download_content)
    page("donate.html", "Donate", donate_content)
    page("bio.html", "About", bio_content)

    (base / "DEPLOY.md").write_text(_deploy_md(), encoding="utf-8")

    return str(output_dir.resolve())
