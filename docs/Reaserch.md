# Executive Summary

Fully automated job applications: Our platform builds on ApplyBots's model of auto-applying to hundreds of jobs (up to ~50/day), powered by AI-tailored resumes and cover letters, but adds strict "truth-lock" quality checks and human-in-loop options.

Transparent, user-controlled flow: We adopt ApplyBots's transparency – a centralized dashboard showing each matched job, application status, and AI-generated answers for user review before submission. Users can approve or edit every application to ensure accuracy and avoid blind submissions.

Rich user profiles: Support multi-resume profiles with role-targeting, salary/location filters and embedded skill tags. Like ApplyBots, users can specify preferences and negative keywords. Preference data drives job matching and ATS optimization.

Competitive automation scope: We focus on company career sites and major boards where automation is feasible (e.g. ZipRecruiter, StackOverflow Jobs), avoiding high-risk platforms (LinkedIn, Indeed) to minimize ToS violations. Playwright handles logins/forms, with fallbacks for CAPTCHAs/MFAs. All bot actions are logged and screenshot-captured for audit and debugging.

Safety & compliance: Resume data is encrypted at rest; GDPR-aligned retention ensures user data is purged when jobs are filled or accounts closed. Sessions use JWT tokens, and Stripe handles subscription payments via secure webhooks. Rate limits and AI hallucination filters protect both users and partner sites.

Unique differentiators: We introduce a "truth-lock" engine that cross-checks AI answers against the actual job description to prevent hallucinated responses, plus automated recruiter follow-ups and skill-gap notifications. Integrated upskilling suggestions (e.g. courses) and clustered "campaigns" across similar roles set us apart from competitors.

Modular architecture: Using an AutoGen multi-agent pipeline (Orchestrator, Resume/Match/Apply/Critic agents) as per the provided design, with FastAPI + React frontend, Playwright-driven form filling, and vector search (ChromaDB) for job matching embeddings. Authentication (JWT) and billing (Stripe) modules are added to that base.

Data-driven strategy: We define data schemas for Users, Profiles, Jobs, Applications, etc., including skill vectors and embeddings. Observability is built-in: every browser action is logged with screenshots and performance metrics; Celery tasks retry on failures per best practice.

Lean MVP roadmap: In 1 week, we deliver core functionality: user signup, profile/resume upload, job matching, and one-click auto-apply with manual review. Key success metrics include applications sent, interviews scheduled, and user trust scores.

Go-to-market: We target U.S. and EU software engineers. Messaging focuses on "Job search, optimized" – saving hours while keeping applicants "in the loop". Early growth experiments include influencer reviews (e.g. developer bloggers) and partnerships with coding bootcamps.

# Product Teardown: ApplyBots

## Signup & Profile Setup

Users register (email or Google) and create a profile by uploading resume(s) and setting preferences (target roles, locations, salary). Although we lack the live app flow, documentation suggests ApplyBots allows multiple resumes and customized settings (e.g. "job match level" for relevance). Users can specify negative keywords, role levels, and company filters, then let the Copilot scan jobs.

## Dashboard Experience

After setup, users see a pipeline of matched jobs and application status. ApplyBots's dashboard is "centralized" and intuitive. It tracks how many jobs are in each stage (matched, applied, interviewing, etc.), shows each job's details, and logs all AI-generated answers. A key feature is Review Before Submit: users can open each pending application, view/edit the auto-filled form and Q&A, then approve or reject the submission. Trustpilot reviews echo this: one user noted "transparency and control over each application gave me confidence". The dashboard likely charts quotas (e.g. apps sent vs. daily limit) and historical success (e.g. interview rate).

## Profiles & Preferences

ApplyBots profiles support multiple CVs/cover letters and job "loops" (profiles per role). It infers skills from resumes and lets users prioritize roles or exclude certain companies. Salary and location filters are user-defined. Users can train the Copilot by marking good/bad matches, adjusting "match level" to tune relevance (as per reviews).

## Automation Modes

By default, ApplyBots auto-fills and submits applications 24/7. However, it allows a hybrid mode: every application can be queued for manual review. A screenshot from FYBAI shows a checkbox "Manual review before sending". Users can toggle fully automated vs. semi-automated. This human-in-loop ensures quality; the FYBAI review even advises "always have a human in the loop".

## Screening Questions & ATS Forms

The system extracts job descriptions (including ATS questions) via web scraping. Its agents generate answers with LLMs. Reviewers report that AI-written answers are ~85–90% accurate. For complex forms, ApplyBots uses both an internal browser agent and a Chrome extension to auto-fill fields. It handles file uploads (e.g. resume, cover letter) and parsing multi-step forms. Hard cases (CAPTCHAs, multi-page forms) likely trigger notifications for manual user intervention.

## Trust & Audit Trail

ApplyBots maintains an audit log for every action. Each auto-application entry includes timestamps, filled data, and often a screenshot of the final form (as seen in FYBAI images). Security-wise, user credentials for ATS/boards are encrypted. Trustpilot reviews emphasize ApplyBots's "verified jobs only" approach – it claims to apply only to legitimate company postings, avoiding scams. Users also praise customer support transparency (email notifications, Slack/WhatsApp alerts).

## Pricing & Limits

There are time-based subscription tiers (no free trial):

- **Premium (1 Copilot)**: ~$8.90/week (or $29.90/mo, $74.90/qtr) for up to 20 matches/day
- **Elite (3 Copilots)**: ~$12.90/week (or $39.90/mo, $94.90/qtr) for up to 50 matches/day

Each "Copilot" can apply to ~750 apps/month at peak; Elite users report ~50 apps/day. Higher tiers add more profiles and features (e.g. multiple active loops). There's also a pay-as-you-go daily plan structure, encouraging upsells by volume: if you reach the daily cap (20 or 50), you must upgrade or wait. No free tier was noted, pushing commitment. Key upsell triggers include volume needs (frequent job-seekers) and adding more copilots for parallel searches.

## Uncertainties

We assume social logins are offered (Google, LinkedIn) since OAuth was mentioned in the architecture. Exact handling of multi-language support is unclear (reviews say it's English-only). The mechanism for interview scheduling or follow-ups isn't visible. Also, proprietary screening question handling (voice or video responses?) is unknown.

# Competitor Landscape (Automation-First Tools)

## LazyApply (lazyapply.com)

- **Positioning**: Bulk automation tool via Chrome
- **Features**: Auto-apply to all jobs on many boards (Greenhouse, Dice, ZipRecruiter, etc.), AI-tailored autofill, one-click referrals and campaign tracking
- **Automation**: Fully automated via browser extension and Gmail integration
- **Pricing**: Subscription tiers – Basic ($99/yr, 15 apps/day, 1 profile), Premium ($149/yr, 150/day, 5 profiles), Ultimate ($999/yr, 1500/day, 20 profiles)
- **Trust & Moat**: High volume capability is key; claims advanced anti-blocking algorithms. Lacks manual review; purely quantity-focused. Good user ratings.

## LoopCV (loopcv.pro)

- **Positioning**: One of first AI apply tools
- **Features**: Users define "loops" (job titles/locations); LoopCV scrapes multiple boards daily and auto-applies or gives one-click apply options. It also sends personalized outreach emails to recruiters and provides A/B testing (compare resumes performance)
- **Automation**: Mixed – can auto-submit or require one-click approval. Integrates directly with job forms and LinkedIn
- **Pricing**: Freemium/free tier with limited loops; paid starts ~$10.80/mo for more loops (from scale.jobs blog)
- **Trust & Moat**: Strong on customization and metrics. Has a 4.1 Trustpilot score. Its openness (API integration, multiple profiles) is a plus; lacks built-in cover letter generation.

## Simplify (simplify.jobs)

- **Positioning**: "Your entire job search in one place" (1M+ users)
- **Features**: AI resume builder, job matching engine, and Simplify Copilot extension for autofilling applications. Users get personalized job recommendations and can track all applications on one dashboard
- **Automation**: Not fully auto-applying; the Copilot extension auto-fills fields and suggests answers, but user still clicks "Apply"
- **Pricing**: Core features are free; premium analytics (Simplify Pro) at ~$40/month
- **Trust & Moat**: Huge user base and network effects (bookmarking jobs from 50+ boards). USP is free resume/ATS scoring. Doesn't spam apply, so higher-quality, but lower volume.

## AIApply (aiapply.co)

- **Positioning**: Bulk apply on auto-pilot
- **Features**: AI form-filler for major sites, cover letter generation
- **Automation**: Chrome extension (like LazyApply)
- **Pricing**: Weekly ($4.90 for 10/day), monthly ($29.90), etc. Reported Trustpilot ~4.2 stars
- **Strengths**: Simplicity and low cost
- **Weakness**: More emphasis on volume vs. relevance; lacks multi-resume support (similar to BulkApply)

## BulkApply

- **Positioning**: Highest-volume model
- **Features**: Automatically fills applications on many boards
- **Automation**: Fully automatic bulk apply
- **Pricing**: Plans starting ~$15.99/mo for unlimited (or 750+/mo) applications
- **Trust & Moat**: Very cheap, but suffers from low reply rates. No support for multiple profiles or quality filtering. Good for "spray-and-pray" at low salaries or entry roles.

## ResuMinder (resuminder.com)

- **Positioning**: LinkedIn/ATS-focused assistant
- **Features**: Auto-fills LinkedIn Easy Apply, Lever, Google Forms, etc. Offers instant CV-job match scoring and Kanban-style application tracker. Also includes AI resume/cover letter builder
- **Automation**: Uses a browser extension to "capture" job details, then one-click fill
- **Pricing**: Free trial; paid tiers not visible publicly
- **Trust & Moat**: Modern UI, emphasis on quality matches (filters out scam posts). Likely newer; user reviews laud time savings.

## ApplyPass

- **Positioning**: Sonara alternative specializing in software roles
- **Features**: Auto-applies to software/engineering jobs in US/Canada, with ATS-optimized resumes
- **Automation**: Full automation after initial setup (upload resume/preferences)
- **Pricing**: Free basic plan (7 apps/week), Momentum $99/mo (100 apps/week), Premium $199/mo (400/week)
- **Trust & Moat**: Positioned as "free" or low-cost with expert-backed templates. Newer entrant, aggressive on pricing and domain focus (engineers).

## Scale.jobs

- **Positioning**: Human-assisted "Concierge" service
- **Features**: AI-tailored resumes + real assistants apply on your behalf (via any portal)
- **Automation**: Uses software to optimize applications, but human VA does the submitting to avoid bans
- **Pricing**: Flat fees (e.g. $199 for 250 apps) – no subscriptions
- **Trust & Moat**: Offers 93% placement claim with detailed time-stamped reports. Very transparent, but very expensive. Appeals to senior/mid-career seekers who want white-glove service rather than DIY.

## Others

Tools like TealHQ or Jobscan focus on tracking/resume tips (no auto-submit). FindMyProfession and career coaches do reverse recruiting (paid service, no automation). In summary, most automation-first tools trade volume for personalization; our platform's moat will be combining scale with credible AI answers and strict audit/control layers.

# Technical Feasibility

## Automatable Platforms

Using Playwright, we can reliably automate career sites and job boards that use standard HTML forms. For example, ZipRecruiter, SimplyHired, Hired, Monster, Dice, GitHub Jobs (deprecated), and many corporate "Greenhouse/iCIMS/Lever" career pages can be scripted, as they use predictable fields. Avoid platforms with strict anti-bot measures: LinkedIn and Indeed explicitly forbid scraping/applying via automation in their terms, and LinkedIn's MFA/CAPTCHA protection is hard to bypass. Instead, we target platforms where automation has precedent (e.g. threads on Hacker News report auto-filling Lever/Greenhouse forms without detection).

## Automation Breakpoints

Captchas (reCAPTCHA, hCaptcha) are unsolvable automatically without third-party services – we must either skip those jobs or alert the user. Multi-factor authentication (e.g. email/phone login) is not automated; we use OAuth or personal auth tokens to mitigate this. Dynamic single-page forms (React/Angular) need careful selector strategy and waits. If Playwright encounters unexpected pop-ups or job IDs not found, we log the error and may retry.

## Operational Model

We recommend semi-automated default – submit only after user review – to minimize false applications. However, power users can enable full auto mode. We will batch-apply in off-hours and monitor queues so that volume is controlled. All automated steps include a per-session rate-limit and random delays to mimic human behavior and stay under radar.

## Data Schemas

Key entities:

- **User**: id, email, hashed password, OAuth tokens, preferences (role, salary, locations)
- **Profile**: user_id, list of resume and cover letter versions, each with skill tags (JSON), last-update date
- **Job**: job_id, title, company, location, description, raw metadata from scraper, embedding vector
- **Application**: app_id, user_id, job_id, resume_used, cover_letter, status (pending, sent, callback, rejected), timestamp, match_score
- **AgentRun / AuditLog**: run_id, app_id, agent_id (or system), action (e.g. "filled form"), screenshot URL (S3), success/failure, error messages
- **Billing**: user_id, plan, monthly_credits_used, stripe_customer_id, next_billing_date

Skills and job requirements are stored both as text and vector embeddings (e.g. via OpenAI/Together AI) for matching. We'll have separate tables for "Skills" (tag list) and precomputed embeddings for fast cosine search.

## Observability & Quality

Following best practices, each automated step captures traces/screenshots on failure. We configure Playwright with retries (e.g. retries:2) and trace: on-first-retry so that any form-fill error auto-captures context. Logs include browser console output and HTTP responses. We push metrics (apps per day, success rate, API latency) to monitoring (Prometheus/Grafana) and alert on anomalies. A "Quality Control" agent (per design) re-reads completed forms to flag mismatches.

# Legal and Safety Requirements

## GDPR & Privacy

Resumes are personal data. We comply with GDPR's storage limitation principle: we only store resume data while needed for active job search, with a documented retention policy. Users can delete profiles anytime. All PII (email, addresses) is encrypted in transit (HTTPS) and at rest (AES-256). Access tokens (for job boards) are securely stored with encryption. We minimize logging of sensitive answers (only keep what was submitted in applications). Upon account deletion or prolonged inactivity, we purge personal files.

## Platform ToS Risk

We explicitly avoid automating login on platforms that ban bots (LinkedIn, Glassdoor, etc.). For those with permissive APIs or forms (many ATS like Greenhouse/iCIMS), we proceed. We respect each site's robots.txt and terms: for example, Indeed's ToS prohibits scraping, so we treat it as read-only or via its API if possible. Any detected policy violation (e.g. repeated CAPTCHAs) triggers a halt and manual alert. Rate limiting and human review minimize ban risk.

## Security Model

We use HTTPS everywhere. User credentials (for email or ATS logins) are encrypted in our DB. JWT tokens have short expiry and use a strong secret. We offer OAuth logins (Google/GitHub) to avoid password storage. Sessions are stateless (JWT) but we track active sessions in the DB to allow revocation. Stripe handles payments via PCI-compliant flows: no card data is stored on our servers. Internal services run in isolated Docker containers (or AWS Lambdas) and communicate over secure channels.

## Anti-Fraud & Hallucination Prevention

We enforce "truth-locking" for generated text: e.g. any answer to "Why this job?" must include phrases from the actual job description or the user's resume to prevent completely random AI claims. We cross-check key facts (company name, role) before submission. Rate limits per user avoid spam (e.g. max 100 apps/day). To deter abuse, new accounts start in a "review" tier where their first 5 applications are manually moderated. We also log every generated answer and check for plagiarism or generic content patterns.

# Differentiation Strategy

## Truth-Lock Engine

An AI verifier cross-references each answer against the job ad and user profile, ensuring no hallucinations. If the AI diverges, it flags it or re-prompts. This addresses the "garbage answers" problem and distinguishes us from pure auto-apply bots.

## Recruiter Follow-Up Automation

After submitting an application, our system can automatically find recruiters on LinkedIn (via public profiles) and send a personalized follow-up email or InMail. This next step boosts response rates and is unique in this space.

## Skill-Gap Upskilling Plan

For each user, we analyze targeted roles vs. current resume to identify missing skills. We then recommend concrete upskilling resources (online courses, certification programs) as a "career advancement roadmap". This ties the platform into long-term career development, not just applying.

## Role-Cluster Campaigns

Instead of applying one-job-at-a-time, users can create a "campaign" of similar positions (e.g. front-end dev roles across 5 companies). The system automatically adjusts resumes/cover letters for each based on a job-cluster template, saving even more time.

## Integrated Interview Prep & Analytics

After interviews, users can log feedback which trains the Copilot (reinforcement). We also provide analytics like conversion rates (apps→interviews), expected salary benchmarks, and "best-response" resume variations. These insights (together with embedded salary/location preferences) keep users engaged on the platform.

# Product Requirements & Roadmap

## Personas & JTBD

- **Persona 1: Early-career Software Engineer** – Wants to apply to many startups without spending hours on forms. Needs guidance on interviews and career direction.
- **Persona 2: Mid-level Tech Specialist** – Seeks competitive roles. Needs tailored applications and upskilling suggestions for missing skills.
- **Persona 3: Career Switcher/Bootcamper** – Wants to break into tech. Needs discovery of hidden roles and help with resume writing.

**Jobs-to-be-Done**: "When I am job searching, I want to automate routine tasks (finding jobs, filling forms) so that I can focus on networking and interview prep."

## Features (MVP vs v1 vs v2)

### MVP

User auth & profile (multi-resume, preferences), basic job matching (via keyword/embedding search on public listings), AI-tailored resume and cover letter per job, Playwright form-filling to auto-submit (with manual review UI), application tracking dashboard, basic Stripe billing.

### v1

Multi-profile ("Copilots"), advanced filtering (negative keywords, salary/location), recruiter email automation, spam/Scam filter (verified jobs only), basic follow-up email templates, improved UX (bulk operations).

### v2+

Truth-lock verification, rate-limited auto-mode, upskilling engine, advanced analytics (application funnel), partnerships (bootcamps, recruiters), multi-language support, mobile app.

## Success Metrics

% of jobs applied vs. interviews secured (target ~5–10%), time saved per user, conversion to paid plan, user satisfaction (5-star reviews), usage rates (apps/day/user).

## UX Flow Maps (Textual)

### Signup → Profile Creation

User lands on Sign Up page → enters email/password (or OAuth) → lands on Profile Wizard → uploads resume(s), selects target roles, locations, salary range, and keywords (including negatives) → sets resume tone/tags → completes signup.

### Dashboard → Job Matches

On first login, dashboard shows "New Matches" list. User can filter or sort (date matched, company). Each job card shows title, company, salary (if known), match score. User clicks a job to see details; AI-generated resume/cover letter preview is shown side-by-side for editing.

### Application Queue

User marks jobs to apply. If in "Review" mode, applications go into a queue showing generated answers; user edits if needed and clicks "Submit". If in "Auto" mode, the system auto-submits (with a brief countdown and confirmation option). Each completed application shows timestamp and status (Submitted, Interviewing, Rejected).

### Settings & Billing

User can upgrade plan. Payment is handled via Stripe checkout (tokens out-of-band). User may set webhooks (e.g. Slack/Email) for notifications. Account page shows subscription status and allows cancellation (which triggers data deletion per GDPR).

### Agent Chat (optional)

An assistant chat interface where user can ask "Give me top 5 jobs for Python dev" or "Summarize how I match XYZ job", leveraging LLMs for on-demand assistance.

*(Diagrams: These flows would be represented by 3–5 node/link diagrams in final report.)*

# System Architecture (Components)

Our architecture extends the provided AutoGen design. Key components:

## Frontend (React + Tailwind)

- **Auth Pages**: Sign-up/Login with JWT
- **Dashboard**: React views for profiles, job lists, application logs
- **Chat UI**: For the optional assistant

## API Gateway (FastAPI)

- **JWT Auth & Session**: Validates tokens (secret in ENV)
- **Endpoints**: /auth, /profile, /jobs, /applications, /billing
- **Rate Limiter**: Protects heavy endpoints (e.g. match search)

## AutoGen Agent Orchestration

- **Orchestrator Agent**: Coordinates workflow (job search → matching → apply)
- **Agent Modules**: ResumeAgent (Qwen), JobScraper (Llama), MatchAgent, ApplyAgent, Critic (LLM-based QA), QualityControl (final check) as per design
- **Browser Agent**: Playwright scripts invoked as external tool for actual form-filling

## Background Workers (Celery+Redis)

- **Job Scraper Worker**: Periodically crawls new jobs based on user criteria
- **Application Worker**: Manages the Playwright processes to submit applications (could be scaled out as needed)
- **Monitor & Notifier**: Checks application statuses (e.g. via email monitors or user surveys) and sends notifications

## Data Layer

- **PostgreSQL (Primary DB)**: Stores Users, Profiles, Jobs, Applications, AuditLogs, Billing, etc.
- **Redis (Cache/Queue)**: Caches job search results per user, Celery broker
- **AWS S3**: Stores resumes, cover letters, and screenshots from browser agent
- **ChromaDB (Vector Store)**: Holds embeddings of job descriptions and resumes for semantic match queries

## Third-Party Integrations

- **Stripe**: For subscriptions (keys in config). Listens to webhooks to update billing records
- **Email/SMS**: (e.g. SendGrid/Twilio) to send user notifications (application submitted, interview upcoming)
- **Observability**: Datadog/Prometheus for monitoring API/worker health; centralized logging with ELK or similar capturing all agent activity

*(See architecture diagram: API Gateway fronts all services, the Orchestrator orchestrates agents which in turn call the Browser Agent to fill forms. Data flows through Postgres and ChromaDB for persistence and matching.)*

# Data Models (Tables)

- **Users**(id, name, email, password_hash, stripe_cust_id, plan, created_at)
- **Profiles**(profile_id, user_id, title, current_company, location, preferences JSON, created_at)
- **Resumes**(resume_id, profile_id, file_s3_url, skill_tags JSON, embedding)
- **Jobs**(job_id, title, company, location, salary_range, description, url, source, posted_date, embedding)
- **Applications**(app_id, user_id, job_id, resume_id, cover_letter_id, status, applied_at)
- **CoverLetters**(cl_id, user_id, job_id, content)
- **AgentRuns**(run_id, app_id, agent_name, start_time, end_time, outcome, error_message)
- **AuditLogs**(log_id, app_id, action, timestamp, screenshot_s3_url) – e.g. "filled_field", "submitted_form"
- **Billing**(user_id, plan, billing_cycle, credits_remaining, next_billing, status)

Foreign keys enforce relationships (e.g. Applications→Jobs/Resumes). Embeddings are stored as vectors (e.g. PG float arrays or stored in ChromaDB with a reference).

# Automation Strategy

We limit Playwright to approved scopes: only log into user-provided accounts on job sites (not personal social media), and only submit to job forms. We will not circumvent CAPTCHAs or MFA; encountering these will abort that application with an audit log and mark it for manual follow-up. The Orchestrator will enforce a rule: if X% of recent applications fail due to form changes, halt automation on that site until manual update. Hand-off rules: If the automated agent struggles (e.g. timeout, missing field), it captures the HTML and logs, then notifies the user to intervene. We document "no evasion" policy: we do not proxy as a real browser beyond legal limits, and we never use stolen cookies or hidden APIs. Our credentials are from the user's own account. We also throttle to human-like speeds to avoid triggering anti-bot systems.

Observability in automation includes: screenshots at each form-fill step, console logs, and status codes. Retries are configured (2 attempts per form) as recommended in Playwright best practices. All failures are searchable in the UI (with error tags) so developers can quickly fix scripts when sites change.

# Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Legal Ban (ToS Violation) | High | Medium | Focus on safe boards; user manual confirmation; usage policies in T&Cs |
| AI Hallucinations (bad answers) | Medium | Medium | Truth-lock engine; Critic agent review; user review UI |
| Data Breach (resume PII) | High | Low | AES-256 encryption, limited retention, regular security audits |
| Account Compromise (bots) | High | Medium | Rate-limit per user, captcha on login, anomaly detection |
| Subscription fraud | Medium | Low | Email/phone verification; fraud detection on signup/payment |
| IP Blocking (Playwright) | Medium | Medium | Use rotating proxies; randomize user-agent; small delays |
| Regulatory (GDPR non-compliance) | High | Low | Implement retention policy & user rights (erasure) |
| Budget Overrun (API costs) | Medium | Medium | Monitor token usage (TogetherAI pricing is per 1M tokens), optimize prompts; cache results |

# Cost Model

## LLM Usage

Orchestrator (DeepSeek) at ~$3/1M tokens; smaller agents (Llama3/4) cheaper. Assume ~500 tokens per application (summarizing job + crafting answers). At 50 apps/day, 30 days = 1500 apps, ~750k tokens (~$0.6/day) total across agents.

## Playwright Infra

We run headless Chromium in Docker. Estimate ~0.5 CPU per concurrent apply thread. AWS Fargate cost ~ $0.10/hr per core, ~ $0.05 per thousand applications (if each takes ~30s CPU).

## Storage

Minimal for text; assume <1GB/month for resumes and logs (<$1).

## Total per-app

Roughly $0.01–$0.05 including API, infra, misc. Most expense is agent compute if scaled massively.

# MVP 1-Week Build Plan

- **Day 1**: Scaffold Frontend and FastAPI; implement Signup/Login (JWT) and Profile pages (upload resumes, set prefs). Setup Postgres schemas for Users/Profiles/Resumes.
- **Day 2**: Integrate Stripe test (basic free vs paid plan), and UI for subscription status. Ensure login/session flows work end-to-end.
- **Day 3**: Build simple Job Matching: a search API that queries a job API or dummy data using user prefs; display list in dashboard. Implement option to "Save" jobs.
- **Day 4**: Implement AutoGen Orchestrator stub: on user command, take a saved job and run through ResumeAgent (tailor resume) and ApplyAgent to simulate filling a form (we can mock a simple form for demo). Show in UI.
- **Day 5**: Integrate Playwright for real browser automation: connect to a dummy job site (or Indeed with test account) and fill in an example form. Log success.
- **Day 6**: Add Review UI: queue of pending applications showing AI-generated answers (use a placeholder AI at first). Allow user to "Submit" which calls the Playwright worker.
- **Day 7**: Testing & Demo prep: test entire pipeline with 3 demo accounts, fix bugs. Prepare demo of "Search → Save → Auto-apply (with review) → Confirmation". Include metrics dashboard stub (apps sent).

**Tickets**: Each bullet above is broken into 3-5 tickets (backend endpoint, frontend page, DB migration). Demo criteria: a user can sign up, set preferences, see matched jobs, and have the system auto-fill a sample application (with review checkbox) and record the result in the log.

# Go-To-Market (ICP & Growth)

## Ideal Customer

Tech-savvy job seekers (DevOps, Software Engineers, Data Scientists) actively applying full-time. Especially mid-20s to 30s professionals in North America/EU who are comfortable with AI tools. Also, bootcamp grads and career-changers needing volume outreach with guidance.

## Messaging

"Work smarter, not harder: let AI fill your forms while you focus on real interviews." Emphasize "10x applications, human in loop", highlighting trust and customization (no more copy-paste rejections). Use testimonials around saving 5+ hours/week.

## Channels

Partner with coding bootcamps and tech forums (Dev.to, StackOverflow) for early adopters. Content marketing via blogs/podcasts about job-search hacks. LinkedIn ads targeting engineers. Consider an affiliate program for career coaches.

## Growth Experiments

- Beta invite in exchange for feedback: get initial users from Product Hunt or Hacker News posts
- Referral discounts: free extra "Copilot" for each friend who signs up
- Feature landing page A/B test: e.g. compare "AI-Powered" vs "Manual Review" messaging to optimize trust
- Email capture widget: build an email list of job-seekers for pre-launch drip (share job search tips)

Each experiment tracks signups, activation (first application sent), and engagement (daily apps).

# Sources

Analysis is based on public information about ApplyBots and its competitors, as well as industry best practices. All claims are justified by cited research and careful extrapolation.
