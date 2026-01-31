"""PDF generator service for resume export.

Standards: python_clean.mdc
- Jinja2 for HTML templating
- WeasyPrint for PDF conversion
- Async operations with proper cleanup
"""

from pathlib import Path
from typing import Literal

import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.domain.resume import ResumeContent
from app.core.ports.storage import FileStorage

logger = structlog.get_logger(__name__)

# Template directory path
TEMPLATES_DIR = Path(__file__).parent / "pdf_templates"


# Resume template HTML (embedded for simplicity)
RESUME_TEMPLATES = {
    "professional-modern": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ content.full_name }} - Resume</title>
    <style>
        @page {
            size: letter;
            margin: 0.5in;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
        }
        .container {
            max-width: 100%;
        }
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 16pt;
            padding-bottom: 12pt;
            border-bottom: 2pt solid #2563eb;
        }
        .name {
            font-size: 24pt;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 6pt;
        }
        .contact-info {
            font-size: 9pt;
            color: #555;
        }
        .contact-info span {
            margin: 0 8pt;
        }
        .links {
            margin-top: 4pt;
            font-size: 9pt;
        }
        .links a {
            color: #2563eb;
            text-decoration: none;
            margin: 0 8pt;
        }
        /* Sections */
        .section {
            margin-bottom: 12pt;
        }
        .section-title {
            font-size: 11pt;
            font-weight: 700;
            color: #1e3a5f;
            text-transform: uppercase;
            letter-spacing: 1pt;
            margin-bottom: 6pt;
            padding-bottom: 3pt;
            border-bottom: 1pt solid #ddd;
        }
        /* Summary */
        .summary {
            font-size: 10pt;
            color: #444;
            line-height: 1.5;
        }
        /* Experience */
        .experience-item {
            margin-bottom: 10pt;
        }
        .experience-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 3pt;
        }
        .job-title {
            font-weight: 600;
            color: #1e3a5f;
        }
        .company {
            color: #333;
        }
        .date-location {
            font-size: 9pt;
            color: #666;
            text-align: right;
        }
        .achievements {
            margin-top: 4pt;
            padding-left: 14pt;
        }
        .achievements li {
            margin-bottom: 2pt;
            font-size: 9.5pt;
        }
        /* Education */
        .education-item {
            margin-bottom: 8pt;
        }
        .degree {
            font-weight: 600;
            color: #1e3a5f;
        }
        .institution {
            color: #333;
        }
        /* Skills */
        .skills-category {
            margin-bottom: 4pt;
        }
        .skills-label {
            font-weight: 600;
            font-size: 9pt;
            color: #1e3a5f;
            display: inline;
        }
        .skills-list {
            font-size: 9pt;
            color: #444;
            display: inline;
        }
        /* Projects */
        .project-item {
            margin-bottom: 8pt;
        }
        .project-name {
            font-weight: 600;
            color: #1e3a5f;
        }
        .project-tech {
            font-size: 8pt;
            color: #666;
            font-style: italic;
        }
        /* Certifications, Awards */
        .cert-item, .award-item {
            margin-bottom: 4pt;
            font-size: 9.5pt;
        }
        /* Languages */
        .language-item {
            display: inline-block;
            margin-right: 16pt;
            font-size: 9.5pt;
        }
        .proficiency {
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="name">{{ content.full_name }}</div>
            <div class="contact-info">
                {% if content.email %}<span>{{ content.email }}</span>{% endif %}
                {% if content.phone %}<span>{{ content.phone }}</span>{% endif %}
                {% if content.location %}<span>{{ content.location }}</span>{% endif %}
            </div>
            {% if content.linkedin_url or content.portfolio_url or content.github_url %}
            <div class="links">
                {% if content.linkedin_url %}<a href="{{ content.linkedin_url }}">LinkedIn</a>{% endif %}
                {% if content.portfolio_url %}<a href="{{ content.portfolio_url }}">Portfolio</a>{% endif %}
                {% if content.github_url %}<a href="{{ content.github_url }}">GitHub</a>{% endif %}
            </div>
            {% endif %}
        </div>

        <!-- Summary -->
        {% if content.professional_summary %}
        <div class="section">
            <div class="section-title">Professional Summary</div>
            <div class="summary">{{ content.professional_summary }}</div>
        </div>
        {% endif %}

        <!-- Experience -->
        {% if content.work_experience %}
        <div class="section">
            <div class="section-title">Professional Experience</div>
            {% for exp in content.work_experience %}
            <div class="experience-item">
                <div class="experience-header">
                    <div>
                        <span class="job-title">{{ exp.title }}</span>
                        <span class="company"> | {{ exp.company }}</span>
                    </div>
                    <div class="date-location">
                        {% if exp.start_date %}{{ exp.start_date }}{% endif %}
                        {% if exp.end_date %} - {{ exp.end_date }}{% elif exp.is_current %} - Present{% endif %}
                        {% if exp.location %} | {{ exp.location }}{% endif %}
                    </div>
                </div>
                {% if exp.achievements %}
                <ul class="achievements">
                    {% for ach in exp.achievements %}
                    <li>{{ ach }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Education -->
        {% if content.education %}
        <div class="section">
            <div class="section-title">Education</div>
            {% for edu in content.education %}
            <div class="education-item">
                <div class="experience-header">
                    <div>
                        <span class="degree">{{ edu.degree }}</span>
                        {% if edu.field_of_study %}<span> in {{ edu.field_of_study }}</span>{% endif %}
                        <span class="institution"> | {{ edu.institution }}</span>
                    </div>
                    <div class="date-location">
                        {% if edu.graduation_date %}{{ edu.graduation_date }}{% endif %}
                        {% if edu.gpa %} | GPA: {{ edu.gpa }}{% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Skills -->
        {% if content.skills.technical or content.skills.soft or content.skills.tools %}
        <div class="section">
            <div class="section-title">Skills</div>
            {% if content.skills.technical %}
            <div class="skills-category">
                <span class="skills-label">Technical: </span>
                <span class="skills-list">{{ content.skills.technical | join(', ') }}</span>
            </div>
            {% endif %}
            {% if content.skills.tools %}
            <div class="skills-category">
                <span class="skills-label">Tools & Technologies: </span>
                <span class="skills-list">{{ content.skills.tools | join(', ') }}</span>
            </div>
            {% endif %}
            {% if content.skills.soft %}
            <div class="skills-category">
                <span class="skills-label">Soft Skills: </span>
                <span class="skills-list">{{ content.skills.soft | join(', ') }}</span>
            </div>
            {% endif %}
        </div>
        {% endif %}

        <!-- Projects -->
        {% if content.projects %}
        <div class="section">
            <div class="section-title">Projects</div>
            {% for proj in content.projects %}
            <div class="project-item">
                <div>
                    <span class="project-name">{{ proj.name }}</span>
                    {% if proj.url %}<a href="{{ proj.url }}" style="font-size: 8pt; color: #2563eb;"> [Link]</a>{% endif %}
                </div>
                <div style="font-size: 9pt; color: #444;">{{ proj.description }}</div>
                {% if proj.technologies %}
                <div class="project-tech">Technologies: {{ proj.technologies | join(', ') }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Certifications -->
        {% if content.certifications %}
        <div class="section">
            <div class="section-title">Certifications</div>
            {% for cert in content.certifications %}
            <div class="cert-item">
                <strong>{{ cert.name }}</strong>
                {% if cert.issuer %} - {{ cert.issuer }}{% endif %}
                {% if cert.date %} ({{ cert.date }}){% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Awards -->
        {% if content.awards %}
        <div class="section">
            <div class="section-title">Awards & Achievements</div>
            {% for award in content.awards %}
            <div class="award-item">
                <strong>{{ award.title }}</strong>
                {% if award.issuer %} - {{ award.issuer }}{% endif %}
                {% if award.date %} ({{ award.date }}){% endif %}
                {% if award.description %}<div style="font-size: 9pt; color: #666;">{{ award.description }}</div>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Languages -->
        {% if content.languages %}
        <div class="section">
            <div class="section-title">Languages</div>
            {% for lang in content.languages %}
            <span class="language-item">
                {{ lang.language }} <span class="proficiency">({{ lang.proficiency.value | capitalize }})</span>
            </span>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Custom Sections -->
        {% for section in content.custom_sections %}
        <div class="section">
            <div class="section-title">{{ section.title }}</div>
            <ul class="achievements">
                {% for item in section.items %}
                <li>{{ item }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>
</body>
</html>
""",
    "classic-traditional": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ content.full_name }} - Resume</title>
    <style>
        @page {
            size: letter;
            margin: 0.75in;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Times New Roman', Times, serif;
            font-size: 11pt;
            line-height: 1.3;
            color: #000;
        }
        .header {
            text-align: center;
            margin-bottom: 14pt;
        }
        .name {
            font-size: 18pt;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2pt;
        }
        .contact-info {
            font-size: 10pt;
            margin-top: 4pt;
        }
        .section {
            margin-bottom: 12pt;
        }
        .section-title {
            font-size: 12pt;
            font-weight: bold;
            text-transform: uppercase;
            border-bottom: 1pt solid #000;
            margin-bottom: 6pt;
            padding-bottom: 2pt;
        }
        .item {
            margin-bottom: 8pt;
        }
        .item-header {
            display: flex;
            justify-content: space-between;
        }
        .item-title {
            font-weight: bold;
        }
        .item-date {
            font-style: italic;
        }
        ul {
            padding-left: 20pt;
            margin-top: 4pt;
        }
        li {
            margin-bottom: 2pt;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{{ content.full_name }}</div>
        <div class="contact-info">
            {{ content.email }}
            {% if content.phone %} • {{ content.phone }}{% endif %}
            {% if content.location %} • {{ content.location }}{% endif %}
        </div>
    </div>

    {% if content.professional_summary %}
    <div class="section">
        <div class="section-title">Objective</div>
        <p>{{ content.professional_summary }}</p>
    </div>
    {% endif %}

    {% if content.work_experience %}
    <div class="section">
        <div class="section-title">Experience</div>
        {% for exp in content.work_experience %}
        <div class="item">
            <div class="item-header">
                <span class="item-title">{{ exp.title }}, {{ exp.company }}</span>
                <span class="item-date">{{ exp.start_date }} - {{ exp.end_date or 'Present' }}</span>
            </div>
            {% if exp.achievements %}
            <ul>
                {% for ach in exp.achievements %}<li>{{ ach }}</li>{% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if content.education %}
    <div class="section">
        <div class="section-title">Education</div>
        {% for edu in content.education %}
        <div class="item">
            <div class="item-header">
                <span class="item-title">{{ edu.degree }}{% if edu.field_of_study %} in {{ edu.field_of_study }}{% endif %}</span>
                <span class="item-date">{{ edu.graduation_date }}</span>
            </div>
            <div>{{ edu.institution }}</div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if content.skills.technical or content.skills.soft or content.skills.tools %}
    <div class="section">
        <div class="section-title">Skills</div>
        <p>{{ (content.skills.technical + content.skills.soft + content.skills.tools) | join(', ') }}</p>
    </div>
    {% endif %}
</body>
</html>
""",
    "tech-minimalist": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ content.full_name }} - Resume</title>
    <style>
        @page {
            size: letter;
            margin: 0.5in;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
            line-height: 1.5;
            color: #1a1a1a;
        }
        .header {
            margin-bottom: 16pt;
        }
        .name {
            font-size: 20pt;
            font-weight: 600;
            letter-spacing: -0.5pt;
        }
        .contact {
            font-size: 8pt;
            color: #666;
            margin-top: 4pt;
        }
        .contact a {
            color: #0066cc;
            text-decoration: none;
        }
        .section {
            margin-bottom: 14pt;
        }
        .section-title {
            font-size: 8pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1pt;
            color: #999;
            margin-bottom: 6pt;
        }
        .exp-item {
            margin-bottom: 10pt;
        }
        .exp-header {
            display: flex;
            justify-content: space-between;
        }
        .exp-title {
            font-weight: 600;
        }
        .exp-company {
            color: #0066cc;
        }
        .exp-date {
            color: #666;
            font-size: 8pt;
        }
        ul {
            padding-left: 16pt;
            margin-top: 4pt;
        }
        li {
            margin-bottom: 2pt;
        }
        .skills-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8pt;
        }
        .skill-category {
            font-size: 8pt;
        }
        .skill-label {
            color: #999;
            text-transform: uppercase;
            font-size: 7pt;
            letter-spacing: 0.5pt;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{{ content.full_name }}</div>
        <div class="contact">
            {{ content.email }}
            {% if content.phone %} / {{ content.phone }}{% endif %}
            {% if content.github_url %} / <a href="{{ content.github_url }}">GitHub</a>{% endif %}
            {% if content.linkedin_url %} / <a href="{{ content.linkedin_url }}">LinkedIn</a>{% endif %}
        </div>
    </div>

    {% if content.professional_summary %}
    <div class="section">
        <div class="section-title">About</div>
        <p>{{ content.professional_summary }}</p>
    </div>
    {% endif %}

    {% if content.work_experience %}
    <div class="section">
        <div class="section-title">Experience</div>
        {% for exp in content.work_experience %}
        <div class="exp-item">
            <div class="exp-header">
                <div><span class="exp-title">{{ exp.title }}</span> @ <span class="exp-company">{{ exp.company }}</span></div>
                <span class="exp-date">{{ exp.start_date }} → {{ exp.end_date or 'Now' }}</span>
            </div>
            {% if exp.achievements %}
            <ul>{% for ach in exp.achievements %}<li>{{ ach }}</li>{% endfor %}</ul>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if content.skills.technical or content.skills.tools %}
    <div class="section">
        <div class="section-title">Tech Stack</div>
        <div class="skills-grid">
            {% if content.skills.technical %}
            <div class="skill-category">
                <div class="skill-label">Languages & Frameworks</div>
                <div>{{ content.skills.technical | join(', ') }}</div>
            </div>
            {% endif %}
            {% if content.skills.tools %}
            <div class="skill-category">
                <div class="skill-label">Tools & Platforms</div>
                <div>{{ content.skills.tools | join(', ') }}</div>
            </div>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {% if content.projects %}
    <div class="section">
        <div class="section-title">Projects</div>
        {% for proj in content.projects %}
        <div class="exp-item">
            <div><strong>{{ proj.name }}</strong>{% if proj.url %} <a href="{{ proj.url }}">[↗]</a>{% endif %}</div>
            <div style="font-size: 8pt; color: #666;">{{ proj.description }}</div>
            {% if proj.technologies %}<div style="font-size: 7pt; color: #999;">{{ proj.technologies | join(' • ') }}</div>{% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if content.education %}
    <div class="section">
        <div class="section-title">Education</div>
        {% for edu in content.education %}
        <div>{{ edu.degree }} — {{ edu.institution }}{% if edu.graduation_date %} ({{ edu.graduation_date }}){% endif %}</div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
""",
}


class PDFGeneratorService:
    """Service for generating PDF resumes from content.

    Uses Jinja2 for HTML templating and WeasyPrint for PDF conversion.
    """

    def __init__(
        self,
        *,
        storage: FileStorage | None = None,
    ) -> None:
        """Initialize PDF generator service.

        Args:
            storage: Optional file storage for uploading generated PDFs
        """
        self._storage = storage
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None,
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def generate_pdf(
        self,
        *,
        content: ResumeContent,
        template_id: str = "professional-modern",
    ) -> bytes:
        """Generate PDF from resume content.

        Args:
            content: Resume content to render
            template_id: Template ID to use

        Returns:
            PDF file as bytes
        """
        # Render HTML
        html_content = self._render_html(content=content, template_id=template_id)

        # Convert to PDF using WeasyPrint
        try:
            from weasyprint import HTML

            pdf_bytes = HTML(string=html_content).write_pdf()

            logger.info(
                "pdf_generated",
                template_id=template_id,
                name=content.full_name,
                size_bytes=len(pdf_bytes),
            )

            return pdf_bytes
        except ImportError:
            logger.warning("weasyprint_not_installed", msg="Returning HTML instead")
            # Fallback: return HTML if WeasyPrint not installed
            return html_content.encode("utf-8")

    async def generate_and_upload(
        self,
        *,
        content: ResumeContent,
        template_id: str = "professional-modern",
        user_id: str,
        draft_id: str,
    ) -> str:
        """Generate PDF and upload to storage.

        Args:
            content: Resume content to render
            template_id: Template ID to use
            user_id: User ID for storage path
            draft_id: Draft ID for storage path

        Returns:
            Presigned URL to the uploaded PDF
        """
        if not self._storage:
            raise ValueError("Storage not configured for PDF upload")

        # Generate PDF
        pdf_bytes = await self.generate_pdf(content=content, template_id=template_id)

        # Create storage key
        safe_name = "".join(c for c in content.full_name if c.isalnum() or c in " -_")[:50]
        key = f"resumes/{user_id}/{draft_id}/{safe_name}.pdf"

        # Upload to storage
        await self._storage.upload(
            key=key,
            data=pdf_bytes,
            content_type="application/pdf",
        )

        # Get presigned URL
        url = await self._storage.get_presigned_url(key=key, expires_in=3600)

        logger.info(
            "pdf_uploaded",
            user_id=user_id,
            draft_id=draft_id,
            key=key,
        )

        return url

    def _render_html(
        self,
        *,
        content: ResumeContent,
        template_id: str,
    ) -> str:
        """Render resume content to HTML.

        Args:
            content: Resume content
            template_id: Template ID

        Returns:
            Rendered HTML string
        """
        # Get template
        template_html = RESUME_TEMPLATES.get(template_id)
        if not template_html:
            template_html = RESUME_TEMPLATES["professional-modern"]
            logger.warning(
                "template_not_found",
                template_id=template_id,
                using="professional-modern",
            )

        # Create Jinja2 template from string
        template = self._jinja_env.from_string(template_html)

        # Render with content
        return template.render(content=content)

    def get_available_templates(self) -> list[dict]:
        """Get list of available templates.

        Returns:
            List of template metadata
        """
        return [
            {
                "id": "professional-modern",
                "name": "Professional Modern",
                "description": "Clean, modern design with balanced whitespace and blue accents",
                "ats_score": 95,
            },
            {
                "id": "classic-traditional",
                "name": "Classic Traditional",
                "description": "Timeless serif design suitable for conservative industries",
                "ats_score": 98,
            },
            {
                "id": "tech-minimalist",
                "name": "Tech Minimalist",
                "description": "Monospace font with grid layout, perfect for developers",
                "ats_score": 92,
            },
            {
                "id": "creative-designer",
                "name": "Creative Designer",
                "description": "Bold typography and creative layout for design roles",
                "ats_score": 85,
            },
            {
                "id": "executive-premium",
                "name": "Executive Premium",
                "description": "Sophisticated design for senior leadership positions",
                "ats_score": 94,
            },
            {
                "id": "academic-research",
                "name": "Academic/Research",
                "description": "Detailed format for academic and research positions",
                "ats_score": 90,
            },
            {
                "id": "entry-level",
                "name": "Entry Level",
                "description": "Focus on education and skills for new graduates",
                "ats_score": 96,
            },
            {
                "id": "two-column",
                "name": "Two Column",
                "description": "Space-efficient two-column layout",
                "ats_score": 88,
            },
            {
                "id": "compact-dense",
                "name": "Compact Dense",
                "description": "Maximum content in minimum space",
                "ats_score": 91,
            },
            {
                "id": "ats-optimized",
                "name": "ATS Optimized",
                "description": "Ultra-simple format designed for maximum ATS compatibility",
                "ats_score": 100,
            },
        ]

    def render_preview_html(
        self,
        *,
        content: ResumeContent,
        template_id: str = "professional-modern",
    ) -> str:
        """Render HTML preview (for frontend display).

        Args:
            content: Resume content
            template_id: Template ID

        Returns:
            HTML string for preview
        """
        return self._render_html(content=content, template_id=template_id)
