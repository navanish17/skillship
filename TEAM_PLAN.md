# Skillship — The Complete Team Playbook

> **Read this first. Read it fully. This is your map for the next 14–16 weeks.**
> Project: AI-Powered School Management System (LMS) for Indian schools.
> Budget: ₹74,999 (Plan 02 — Agentic AI). Timeline: 14–16 weeks.
> Team: 4 people. Method: **Agile / Scrum-lite with 2-week sprints**.

---

## Table of Contents

1. [What we are building (in plain English)](#1-what-we-are-building)
2. [The Team and Who Owns What](#2-the-team-and-who-owns-what)
3. [Tech Stack Decision (and Why)](#3-tech-stack-decision-and-why)
4. [The Complete Folder Structure](#4-the-complete-folder-structure)
5. [How the Pieces Talk to Each Other](#5-how-the-pieces-talk-to-each-other)
6. [Agile Workflow — Sprints, Standups, Tickets](#6-agile-workflow)
7. [Git Workflow (branches, commits, PRs)](#7-git-workflow)
8. [Sprint-by-Sprint Roadmap (14 weeks)](#8-sprint-by-sprint-roadmap)
9. [API Contract Rules (so nobody blocks anybody)](#9-api-contract-rules)
10. [Tools Everyone Must Install](#10-tools-everyone-must-install)
11. [The "Golden Rules" for Production Quality](#11-golden-rules)
12. [How to Add a New Feature End-to-End](#12-how-to-add-a-new-feature)
13. [Security, Multi-Tenancy, and Data Isolation](#13-security-multi-tenancy)
14. [Testing Strategy](#14-testing-strategy)
15. [Deployment & CI/CD](#15-deployment-cicd)
16. [Definition of Done (DoD)](#16-definition-of-done)
17. [Risks & How We Handle Them](#17-risks)

---

## 1. What We Are Building

Imagine a school buys our software. Their principal, teachers, and students all log in to **one website**. What they see depends on their role:

- **Main Admin** (Skillship team): Controls everything. Adds new schools. Sets prices.
- **Sub Admin** (our manager): Builds question banks, approves quizzes, manages schools.
- **Principal** (school leader): Sees dashboards of their whole school.
- **Teacher**: Creates classes, assigns quizzes, tracks students.
- **Student**: Takes quizzes, gets AI career advice, earns badges.

**The magic** = AI runs behind every screen. When a student takes a quiz, the AI picks harder questions if they're doing well. When a teacher uploads a PDF, the AI turns it into quiz questions. Every week, the AI writes a report for the Principal automatically.

**Non-negotiable rules** (from the proposal):
- School A **cannot** see any data from School B. Ever. (Multi-tenant isolation)
- No public signups. Only admins create users.
- Five roles with strict permissions (RBAC).
- AI is **real** — not a chatbot bolted on the side.

---

## 2. The Team and Who Owns What

| Person | Primary Role | Folders They Own | Secondary |
|---|---|---|---|
| **Navanish** | Backend + AI Lead | `apps/api/` (API routes, services, middleware), `apps/ai-service/` (agents) | Code reviews for Prashant |
| **Prashant** | Backend + AI Engineer | `apps/api/` (auth, quiz engine, jobs), `apps/ai-service/` (RAG, engines) | Code reviews for Navanish |
| **Vishal** | Data Engineer | `packages/db/` (Prisma schema, migrations, seed), `apps/api/src/services/analytics.service.ts`, reports module | Writes all SQL views, tuning queries |
| **Pranav** | Frontend / UI-UX | `apps/web/` entirely (Next.js app), `packages/config/tailwind.config.base.js` | Figma designs, component library |

**Nobody touches somebody else's folder without a PR review.** This is THE most important rule for parallel work.

### Shared ownership (needs 2 reviewers)
- `packages/types/` — the "contract" between frontend and backend. **Vishal proposes, Navanish + Pranav approve**.
- `docs/api/openapi.yaml` — the API spec. **Backend writes, Frontend reviews**.
- `docker-compose.yml`, `.github/workflows/` — **Navanish owns, everyone can suggest**.

---

## 3. Tech Stack Decision (and Why)

| Layer | Tech | Why this and not something else |
|---|---|---|
| **Monorepo** | Turborepo + pnpm workspaces | One repo. Fast builds. Shared types. Industry standard (Vercel, Shopify use it). |
| **Frontend** | Next.js 14 (App Router) + TypeScript | SSR for SEO (public website), built-in routing, React Server Components, Vercel-ready. |
| **UI Library** | TailwindCSS + shadcn/ui + Radix | Not a heavy framework. Copy-paste components we can customize. Figma-accurate. |
| **State Mgmt** | Zustand + TanStack Query | Zustand for UI state, TanStack Query for server state. No Redux boilerplate. |
| **Backend API** | Node.js + Express + TypeScript | Well-known, huge ecosystem, easy to hire for, pairs well with Prisma. |
| **AI Service** | Python + FastAPI | Python has the best AI ecosystem (LangChain, LangGraph, transformers). Separate service so it scales independently. |
| **AI Models** | Claude 4.5 Sonnet (primary), Gemini (fallback/cheap) | Claude for quality tasks (career paths, reports). Gemini for bulk (question generation). |
| **Agent Framework** | LangGraph + Claude Agent SDK | For multi-agent orchestration (Plan 02). Production-ready. |
| **Database** | PostgreSQL 16 | ACID, row-level security for multi-tenancy, JSON columns for flexible AI data. |
| **ORM** | Prisma | Type-safe, great migrations, works beautifully with TS monorepo. |
| **Cache / Queue** | Redis + BullMQ | BullMQ for background jobs (risk alerts, weekly reports, email). Redis for session cache. |
| **Vector DB** | pgvector (Postgres extension) | Don't add a new service. pgvector is enough for RAG at school scale. |
| **Auth** | JWT (access 15min) + Refresh tokens (7 days) + bcrypt | Stateless API, refresh rotation, rate limiting. |
| **File Storage** | Supabase Storage / S3 | Cheap, CDN built-in, signed URLs for private files. |
| **Email / OTP** | Resend | Developer-friendly API, cheap, reliable. |
| **Testing** | Vitest (unit) + Playwright (E2E) + pytest (Python) | Fast, modern, great DX. |
| **Observability** | Pino (logs) + Sentry (errors) + PostHog (product analytics) | Free tiers cover us easily. |
| **CI/CD** | GitHub Actions | Free for us, standard, tons of examples. |
| **Hosting** | Hetzner VPS (Docker Compose) for dev, DigitalOcean droplet for prod | Cheapest that meets Plan 02 requirements. Per proposal. |

---

## 4. The Complete Folder Structure

Here is **every folder, every file, what it does, and who owns it**. This is the north star.

```
skillship/                                   ← repo root
│
├── apps/                                    ← deployable applications
│   │
│   ├── api/                                 ← 🔶 NAVANISH + PRASHANT
│   │   ├── src/
│   │   │   ├── config/                      ← env loading, constants
│   │   │   │   ├── env.ts                   ← validates process.env using zod
│   │   │   │   ├── constants.ts             ← app-wide constants
│   │   │   │   └── logger.ts                ← pino logger setup
│   │   │   │
│   │   │   ├── controllers/                 ← HTTP handlers (thin — just parse & call service)
│   │   │   │   ├── auth.controller.ts
│   │   │   │   ├── school.controller.ts
│   │   │   │   ├── user.controller.ts
│   │   │   │   ├── class.controller.ts
│   │   │   │   ├── course.controller.ts
│   │   │   │   ├── quiz.controller.ts
│   │   │   │   ├── question.controller.ts
│   │   │   │   ├── attempt.controller.ts
│   │   │   │   ├── analytics.controller.ts
│   │   │   │   ├── report.controller.ts
│   │   │   │   ├── career.controller.ts     ← proxies to AI service
│   │   │   │   └── notification.controller.ts
│   │   │   │
│   │   │   ├── routes/                      ← Express routers — just wire URL → controller
│   │   │   │   ├── auth.routes.ts
│   │   │   │   ├── school.routes.ts
│   │   │   │   ├── quiz.routes.ts
│   │   │   │   ├── analytics.routes.ts
│   │   │   │   ├── report.routes.ts
│   │   │   │   └── index.ts                 ← combines all routers
│   │   │   │
│   │   │   ├── middleware/                  ← cross-cutting concerns
│   │   │   │   ├── auth.middleware.ts       ← verifies JWT, attaches req.user
│   │   │   │   ├── rbac.middleware.ts       ← role-based access (requireRole('TEACHER'))
│   │   │   │   ├── tenant.middleware.ts     ← injects schoolId filter everywhere
│   │   │   │   ├── ratelimit.middleware.ts  ← Redis-based rate limit
│   │   │   │   ├── validate.middleware.ts   ← zod schema validator
│   │   │   │   └── error.middleware.ts      ← global error handler → JSON
│   │   │   │
│   │   │   ├── services/                    ← business logic (fat layer — all rules live here)
│   │   │   │   ├── auth.service.ts          ← login, refresh, password reset
│   │   │   │   ├── school.service.ts
│   │   │   │   ├── user.service.ts
│   │   │   │   ├── quiz.service.ts          ← quiz CRUD, approval workflow
│   │   │   │   ├── attempt.service.ts       ← start/submit quiz, scoring
│   │   │   │   ├── analytics.service.ts     ← 🟢 VISHAL contributes here
│   │   │   │   ├── report.service.ts        ← PDF/Excel generation — 🟢 VISHAL
│   │   │   │   ├── ai-bridge.service.ts     ← HTTP client to ai-service
│   │   │   │   ├── storage.service.ts       ← S3/Supabase upload
│   │   │   │   ├── email.service.ts         ← Resend wrapper
│   │   │   │   └── notification.service.ts
│   │   │   │
│   │   │   ├── jobs/                        ← BullMQ background workers
│   │   │   │   ├── queue.ts                 ← queue definitions
│   │   │   │   ├── risk-alert.job.ts        ← runs nightly, detects at-risk students
│   │   │   │   ├── weekly-report.job.ts     ← runs Sundays, AI-generated Principal report
│   │   │   │   ├── report.job.ts            ← async PDF generation
│   │   │   │   └── email.job.ts             ← retries failed emails
│   │   │   │
│   │   │   ├── utils/                       ← pure helper functions
│   │   │   │   ├── crypto.ts                ← hash/compare passwords
│   │   │   │   ├── jwt.ts                   ← sign/verify tokens
│   │   │   │   ├── date.ts
│   │   │   │   └── pagination.ts
│   │   │   │
│   │   │   ├── schemas/                     ← zod validation schemas (request bodies)
│   │   │   │   ├── auth.schema.ts
│   │   │   │   ├── quiz.schema.ts
│   │   │   │   └── ...
│   │   │   │
│   │   │   └── server.ts                    ← entry point: Express app + middleware chain
│   │   │
│   │   ├── test/                            ← integration tests (hits real DB)
│   │   │   ├── setup.ts                     ← spins up test DB
│   │   │   ├── auth.test.ts
│   │   │   ├── quiz.test.ts
│   │   │   └── fixtures/
│   │   │
│   │   ├── Dockerfile                       ← prod image
│   │   ├── Dockerfile.dev                   ← dev hot-reload image
│   │   ├── .env.example
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── ai-service/                          ← 🔶 NAVANISH + PRASHANT
│   │   ├── app/
│   │   │   ├── main.py                      ← FastAPI entrypoint
│   │   │   ├── config.py                    ← env, model IDs, API keys
│   │   │   ├── deps.py                      ← dependency injection (DB client, LLM client)
│   │   │   │
│   │   │   ├── routers/                     ← FastAPI routers (the service's HTTP surface)
│   │   │   │   ├── career.py                ← POST /career/analyze
│   │   │   │   ├── quiz.py                  ← POST /quiz/adaptive-next
│   │   │   │   ├── content.py               ← POST /content/generate-questions
│   │   │   │   ├── tutor.py                 ← POST /tutor/ask (Plan 02)
│   │   │   │   ├── risk.py                  ← POST /risk/scan-school
│   │   │   │   └── reports.py               ← POST /reports/weekly-insight
│   │   │   │
│   │   │   ├── agents/                      ← individual LangGraph agents
│   │   │   │   ├── career_pilot.py          ← career guidance agent
│   │   │   │   ├── tutor_agent.py           ← subject doubt solver
│   │   │   │   ├── analyst_agent.py         ← writes Principal reports
│   │   │   │   ├── risk_agent.py            ← flags disengagement
│   │   │   │   ├── content_agent.py         ← auto-tags content
│   │   │   │   └── orchestrator.py          ← 🌟 multi-agent coordinator (Plan 02)
│   │   │   │
│   │   │   ├── engines/                     ← deterministic ML/algorithms (not LLM)
│   │   │   │   ├── adaptive_quiz.py         ← IRT-style difficulty selector
│   │   │   │   ├── question_gen.py          ← PDF → MCQs pipeline
│   │   │   │   └── scoring.py
│   │   │   │
│   │   │   ├── rag/                         ← Retrieval-Augmented Generation
│   │   │   │   ├── embedder.py              ← creates embeddings (OpenAI/local)
│   │   │   │   ├── retriever.py             ← queries pgvector
│   │   │   │   └── chunker.py               ← splits PDFs/docs
│   │   │   │
│   │   │   ├── prompts/                     ← all LLM prompts (version-controlled!)
│   │   │   │   ├── career.py
│   │   │   │   ├── tutor.py
│   │   │   │   └── report.py
│   │   │   │
│   │   │   └── models/                      ← pydantic request/response models
│   │   │       └── schemas.py
│   │   │
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── .env.example
│   │   └── requirements.txt
│   │
│   └── web/                                 ← 🔷 PRANAV
│       ├── src/
│       │   ├── app/                         ← Next.js App Router
│       │   │   ├── (public)/                ← no auth required
│       │   │   │   ├── page.tsx             ← homepage (SEO-critical)
│       │   │   │   ├── marketplace/         ← browse courses
│       │   │   │   ├── pricing/
│       │   │   │   └── about/
│       │   │   │
│       │   │   ├── (auth)/                  ← login flow
│       │   │   │   ├── login/page.tsx
│       │   │   │   ├── forgot-password/
│       │   │   │   └── layout.tsx
│       │   │   │
│       │   │   ├── (dashboard)/             ← protected, role-gated
│       │   │   │   ├── layout.tsx           ← sidebar + topbar shell
│       │   │   │   │
│       │   │   │   ├── admin/               ← MAIN_ADMIN only
│       │   │   │   │   ├── schools/
│       │   │   │   │   ├── subscriptions/
│       │   │   │   │   └── ai-config/
│       │   │   │   │
│       │   │   │   ├── sub-admin/           ← SUB_ADMIN only
│       │   │   │   │   ├── question-bank/
│       │   │   │   │   ├── quiz-review/
│       │   │   │   │   └── content/
│       │   │   │   │
│       │   │   │   ├── principal/           ← PRINCIPAL only
│       │   │   │   │   ├── overview/        ← school-wide dashboard
│       │   │   │   │   ├── analytics/
│       │   │   │   │   ├── benchmarks/
│       │   │   │   │   └── reports/
│       │   │   │   │
│       │   │   │   ├── teacher/             ← TEACHER only
│       │   │   │   │   ├── classes/
│       │   │   │   │   ├── quizzes/
│       │   │   │   │   ├── students/
│       │   │   │   │   └── insights/
│       │   │   │   │
│       │   │   │   └── student/             ← STUDENT only
│       │   │   │       ├── home/
│       │   │   │       ├── quizzes/
│       │   │   │       ├── courses/
│       │   │   │       ├── career-pilot/    ← AI career guidance
│       │   │   │       ├── tutor/           ← AI doubt solver (Plan 02)
│       │   │   │       └── badges/
│       │   │   │
│       │   │   ├── api/                     ← Next.js API routes (BFF — only if needed)
│       │   │   ├── globals.css
│       │   │   ├── layout.tsx               ← root layout
│       │   │   └── not-found.tsx
│       │   │
│       │   ├── components/
│       │   │   ├── ui/                      ← shadcn primitives (Button, Input, Card)
│       │   │   ├── common/                  ← shared (Sidebar, Topbar, Avatar, etc.)
│       │   │   ├── auth/                    ← LoginForm, etc.
│       │   │   ├── quiz/                    ← QuizPlayer, QuestionCard, Timer
│       │   │   ├── analytics/               ← Chart wrappers (Recharts)
│       │   │   ├── ai/                      ← CareerPilotPanel, TutorChat
│       │   │   └── tables/                  ← DataTable using TanStack Table
│       │   │
│       │   ├── hooks/                       ← custom React hooks
│       │   │   ├── useAuth.ts               ← auth state + login/logout
│       │   │   ├── useQuizzes.ts
│       │   │   ├── useAnalytics.ts
│       │   │   └── useRole.ts               ← role-based gating
│       │   │
│       │   ├── lib/
│       │   │   ├── api.ts                   ← axios/fetch client with interceptors
│       │   │   ├── auth.ts                  ← token storage, refresh logic
│       │   │   ├── store.ts                 ← Zustand stores
│       │   │   ├── utils.ts                 ← cn(), date fmt, etc.
│       │   │   └── query-client.ts          ← TanStack Query setup
│       │   │
│       │   ├── types/                       ← frontend-only types (UI state, etc.)
│       │   │   └── index.ts
│       │   │
│       │   └── middleware.ts                ← Next.js edge middleware (route guards)
│       │
│       ├── public/                          ← static assets
│       ├── .env.example
│       ├── next.config.ts
│       ├── tailwind.config.ts
│       ├── package.json
│       └── tsconfig.json
│
├── packages/                                ← shared libraries
│   │
│   ├── db/                                  ← 🟢 VISHAL OWNS THIS
│   │   ├── prisma/
│   │   │   ├── schema.prisma                ← ⭐ THE SINGLE SOURCE OF TRUTH for data
│   │   │   ├── migrations/                  ← auto-generated, checked into git
│   │   │   │   └── 20260417000000_init/
│   │   │   ├── seed.ts                      ← test data: 1 school, sample users/quizzes
│   │   │   └── rls-policies.sql             ← Postgres Row Level Security rules
│   │   ├── src/
│   │   │   ├── client.ts                    ← export const prisma = new PrismaClient()
│   │   │   └── index.ts                     ← re-exports
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── types/                               ← 📘 SHARED CONTRACT (FE + BE both import)
│   │   ├── src/
│   │   │   ├── user.types.ts                ← User, Role enum
│   │   │   ├── school.types.ts
│   │   │   ├── quiz.types.ts                ← Quiz, Question, Attempt
│   │   │   ├── api.types.ts                 ← request/response DTOs
│   │   │   ├── ai.types.ts                  ← AI service contracts
│   │   │   └── index.ts                     ← barrel export
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── config/                              ← shared configs
│       ├── eslint.config.js
│       ├── tailwind.config.base.js          ← brand colors, spacing scale
│       ├── tsconfig.base.json
│       └── package.json
│
├── docs/                                    ← 📚 living documentation
│   ├── adr/                                 ← Architecture Decision Records (why we chose X)
│   │   ├── 001-tech-stack.md
│   │   ├── 002-multitenancy-strategy.md
│   │   └── 003-ai-service-boundary.md
│   ├── ai/
│   │   ├── prompts.md                       ← prompt library with version history
│   │   └── agents.md                        ← what each agent does
│   └── api/
│       └── openapi.yaml                     ← the API contract (Swagger)
│
├── .github/
│   └── workflows/
│       ├── ci.yml                           ← runs on every PR: lint, test, typecheck
│       └── deploy.yml                       ← on merge to main: build + deploy
│
├── docker-compose.yml                       ← local dev: postgres + redis + all 3 apps
├── docker-compose.prod.yml                  ← production stack
├── .env.example                             ← template for root env vars
├── .gitignore
├── .nvmrc                                   ← Node version pin
├── README.md                                ← setup instructions for new devs
├── TEAM_PLAN.md                             ← ⭐ THIS FILE
├── package.json                             ← pnpm workspace root
├── pnpm-workspace.yaml
└── turbo.json                               ← Turborepo pipeline config
```

---

## 5. How the Pieces Talk to Each Other

```
┌─────────────────┐      HTTPS       ┌─────────────────┐
│  Next.js (web)  │ ───────────────▶ │  Node API       │
│  Browser        │ ◀─── JSON ────── │  Express        │
└─────────────────┘                  └────────┬────────┘
      PRANAV                                  │
                                              │ 1. Prisma (SQL)
                                              │ 2. HTTP (internal)
                                              │ 3. BullMQ (queue)
                                              ▼
                        ┌─────────────────────────────────┐
                        │                                 │
                 ┌──────▼────────┐         ┌──────────────▼─────┐
                 │  PostgreSQL   │         │  FastAPI (Python)  │
                 │  + pgvector   │         │  AI Agents + RAG   │
                 │  VISHAL       │         │  NAVANISH/PRASHANT │
                 └───────────────┘         └────────┬───────────┘
                                                    │
                                                    │ LLM calls
                                                    ▼
                                        ┌──────────────────────┐
                                        │ Claude 4.5 + Gemini  │
                                        └──────────────────────┘
```

### The communication rules (MEMORIZE THESE):

1. **Frontend NEVER talks to AI service directly.** It goes through the Node API. (Why: auth, rate limiting, audit logs all live in Node.)
2. **Node API talks to AI service over internal HTTP** using a shared secret header (`X-Internal-Key`).
3. **AI service NEVER writes to the main DB directly** — it asks Node API to write. (Why: business rules must run through one place.)
   - Exception: embeddings table in pgvector — AI service writes, Node API reads.
4. **Shared types package (`@skillship/types`) is the contract.** If a field changes, it changes in one place.
5. **Background jobs** (risk alerts, reports) run in Node API's BullMQ workers, which call AI service for heavy lifting.

---

## 6. Agile Workflow

We run **2-week sprints**, Scrum-lite (we are 4, not 12 — we skip ceremonies that don't scale down).

### Daily (Mon–Sat, 15 minutes, 10:00 AM IST — Google Meet)
Each person answers 3 questions:
1. What did I finish yesterday?
2. What am I doing today?
3. Am I blocked on anyone? (← most important question)

**Rule**: if the answer to #3 is yes, open a quick 15-min call right after standup. Don't wait.

### Sprint Planning (every 2 weeks, Monday, 1 hour)
- Review what's in the product backlog (list of features from the proposal).
- Pick items for the next sprint based on velocity (how much we finished last time).
- Break items into tasks ≤ 1 day each. If a task > 1 day, split it.
- Assign tasks. Estimate in story points (1, 2, 3, 5, 8 — Fibonacci).

### Sprint Review + Retro (every 2 weeks, Friday of sprint end, 1 hour)
- 30 min: Demo what's done. Each person shares screen, walks through their feature.
- 30 min: Retro — what went well / what didn't / one thing to change next sprint.

### Tool: **Linear** (or free: GitHub Projects)
- Columns: Backlog → Sprint → In Progress → In Review → Done
- Ticket format: `[SKILL-123] Implement quiz submission endpoint`
- Every ticket has: description, acceptance criteria, estimate, assignee.
- **Every PR must reference a ticket** (e.g., branch = `feature/SKILL-123-quiz-submit`).

### Communication channels (Slack or Discord — free)
- `#general` — team chat
- `#standup` — async updates if someone missed the call
- `#backend` — Navanish + Prashant + Vishal
- `#frontend` — Pranav + Navanish (API questions)
- `#ai` — AI agent discussion
- `#deploys` — CI/CD notifications (webhook from GitHub Actions)
- `#client` — when Skillship (the client) asks something

---

## 7. Git Workflow

We use **GitHub Flow with a `develop` branch** (a.k.a. lightweight Git Flow).

### Branches
- `main` — production. Only merged into via PR from `develop`. Every merge auto-deploys.
- `develop` — staging. Features merge here first. Auto-deploys to staging.
- `feature/SKILL-123-short-desc` — your working branch. Branches off `develop`.
- `fix/SKILL-234-bug-desc` — bug fixes.
- `hotfix/SKILL-999-critical` — emergency production fix (branches off `main`, merges back to both).

### Commit messages — Conventional Commits
Format: `<type>(<scope>): <subject>`

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`

Examples:
- `feat(quiz): add adaptive difficulty selection`
- `fix(auth): prevent token leak in refresh flow`
- `chore(db): add migration for career_profile table`

### The PR process (non-negotiable)
1. **Branch off `develop`**: `git checkout -b feature/SKILL-123-student-dashboard develop`
2. **Commit often**, push daily (backup!).
3. **Open a Draft PR early** — helps teammates see what's coming.
4. **Before marking "Ready for Review":**
   - `pnpm lint` passes
   - `pnpm test` passes
   - `pnpm build` passes
   - Self-review your own diff on GitHub (read every line)
   - PR description explains **what** and **why**
   - Linked Linear ticket
5. **Request reviewers**:
   - Frontend PRs → Pranav + (one backend person if it touches API types)
   - Backend PRs → Navanish + Prashant
   - DB PRs → Vishal + Navanish (migrations are destructive — double-check)
6. **Merge requires**: 1 approval + all CI green. Use **Squash Merge** (keeps history clean).
7. **Delete branch after merge.**

### Protected branches (set in GitHub settings)
- `main` and `develop` cannot be pushed to directly. Only via PR.
- Require status checks to pass.
- Require 1 approval.

---

## 8. Sprint-by-Sprint Roadmap

We have ~7 sprints (Sprint 0 + Sprints 1–6 ≈ 14 weeks, with buffer for Sprint 7 launch).

### Sprint 0 — Foundation (Week 1)
**Goal: Everyone can run the full stack locally.**

| Owner | Deliverables |
|---|---|
| Navanish | Monorepo setup (Turborepo + pnpm). Root configs. CI pipeline skeleton. Docker Compose with Postgres + Redis. |
| Prashant | AI service skeleton (FastAPI boots, one `/health` endpoint). LLM client with Claude + Gemini. |
| Vishal | Full Prisma schema designed (all tables). First migration. Seed script with 1 school, 5 users (one per role), 2 sample quizzes. |
| Pranav | Next.js skeleton. Design system tokens from Figma. shadcn/ui installed. Login page UI (no backend yet). |

**Sprint 0 exit criteria**: `pnpm dev` starts all 3 apps. You can log in (mocked). DB has seed data. CI passes.

### Sprint 1 — Auth + User Management (Week 2–3)
**Goal: All 5 roles can log in and see their (empty) dashboard.**

| Owner | Deliverables |
|---|---|
| Navanish | `/auth/login`, `/auth/refresh`, `/auth/logout`. JWT + refresh tokens. Password reset. |
| Prashant | RBAC middleware. Tenant middleware (schoolId auto-injection). Rate limiting. |
| Vishal | User CRUD endpoints. School CRUD. Bulk user import from CSV. |
| Pranav | Login flow (real API). Role-based dashboard routing. Sidebar per role. Profile page. |

### Sprint 2 — Classes + Content + Question Bank (Week 4–5)
**Goal: Sub-admin can build question banks. Teacher can create classes.**

| Owner | Deliverables |
|---|---|
| Navanish | Quiz CRUD + approval workflow (Draft → Review → Published). |
| Prashant | Question bank APIs. Bulk question import. |
| Vishal | Class management APIs. Enrollment APIs. Content upload to S3/Supabase. |
| Pranav | Question bank UI. Class management UI. Quiz builder (drag-drop). |

### Sprint 3 — Quiz Engine + Scoring (Week 6–7)
**Goal: Student can take a quiz end-to-end. Rankings work.**

| Owner | Deliverables |
|---|---|
| Navanish | Quiz attempt start/submit. Auto-grading. Anti-cheat: question randomization. |
| Prashant | Quiz assignment to class. Timer enforcement server-side. |
| Vishal | Analytics tables + materialized views for rankings, skill-wise scores. |
| Pranav | QuizPlayer component with timer. Results screen. Class leaderboard. |

### Sprint 4 — AI Integration Sprint (Week 8–10) ⭐
**Goal: Every "✓ AI" feature from Plan 02 works on staging.**

| Owner | Deliverables |
|---|---|
| Navanish | AI Career Pilot agent (LangGraph). Adaptive quiz engine integration. |
| Prashant | RAG pipeline for content (PDF → embeddings → pgvector). AI Question Generator (PDF → MCQs). Doubt Solver (Tutor agent). |
| Vishal | Risk detection materialized view. Weekly report data aggregation queries. |
| Pranav | Career Pilot dashboard panel. AI tutor chat UI. "Generate questions from PDF" flow. Risk alert notifications. |
| All | Multi-agent orchestrator (Plan 02 centerpiece). |

### Sprint 5 — Analytics + Reports + Badges (Week 10–11)
**Goal: Principal gets real dashboards. Students earn badges.**

| Owner | Deliverables |
|---|---|
| Navanish | Report generation job (async BullMQ). PDF + Excel export. |
| Prashant | AI-written weekly insight report (Analyst agent). |
| Vishal | School benchmarking queries. Monthly/yearly trends. Badge criteria engine. |
| Pranav | Principal dashboard (charts, filters). Report download UI. Badge showcase. |

### Sprint 6 — QA + Hardening + Perf (Week 12–13)
**Goal: Zero P0 bugs. Handles 500 concurrent users. Security audit done.**

| Owner | Deliverables |
|---|---|
| Navanish | Load testing with k6. Fix bottlenecks. Security audit (OWASP top 10). |
| Prashant | AI accuracy evaluation (quiz generation quality, career path relevance). |
| Vishal | DB query optimization (EXPLAIN ANALYZE everything). Indexes. |
| Pranav | E2E tests (Playwright). Accessibility pass. Mobile responsive QA. |

### Sprint 7 — Staging Demo + Production Launch (Week 14–16)
- Week 14: Full client walkthrough on staging. Fix feedback.
- Week 15: Deploy to production. DNS, SSL, monitoring.
- Week 16: Buffer + AI model fine-tuning. Handover docs.

---

## 9. API Contract Rules

**The #1 reason parallel work fails is because backend and frontend disagree on the API shape.** Fix this by making the contract the source of truth.

### Rule 1: Types live in `packages/types/`
Every request body, response body, and DTO is defined once, imported by both FE and BE.

### Rule 2: OpenAPI spec is the public contract
`docs/api/openapi.yaml` is updated **before** implementation starts. Pranav reads it to mock responses while backend is building.

### Rule 3: Mock-first development
- When starting Sprint N, backend writes the OpenAPI spec first.
- Pranav uses **MSW (Mock Service Worker)** to mock the endpoints in the frontend.
- Pranav builds UI against mocks while backend builds the real thing.
- When backend deploys to staging, Pranav removes mocks. If contract is right, **zero** integration surprises.

### Rule 4: Semantic versioning for breaking changes
If you must change an API response shape after it ships:
- Add a new field, don't remove the old one (yet).
- Deprecate the old field with a comment.
- Remove after 2 sprints.

### Rule 5: Every error has a stable code
Instead of just HTTP 400, return:
```
{ "error": { "code": "QUIZ_ALREADY_SUBMITTED", "message": "..." } }
```
Frontend switches on `code`, not message. This prevents UI breaking when we rephrase errors.

---

## 10. Tools Everyone Must Install

### Every person
- **Node.js 20 LTS** (use `nvm` to manage versions) — check `.nvmrc`
- **pnpm 9** (`npm i -g pnpm`)
- **Docker Desktop** (for Postgres + Redis locally)
- **Git** + **GitHub CLI** (`gh`)
- **VS Code** with these extensions:
  - ESLint, Prettier, Tailwind IntelliSense, Prisma, GitLens, Error Lens, Thunder Client (API testing)
- **Linear** account (or GitHub Projects)
- **Slack/Discord** account

### Backend (Navanish, Prashant)
- **Python 3.11+**, `uv` (fast pip replacement)
- **Postman** or **Thunder Client** for API testing
- **TablePlus** or **pgAdmin** for DB inspection
- **Redis Insight** for cache inspection
- **ngrok** (for testing webhooks locally)

### Data (Vishal)
- **DBeaver** or **TablePlus**
- **pgAdmin** (for admin work)
- Prisma CLI (comes with the repo)
- Understanding of: SQL EXPLAIN, indexes, views, RLS

### Frontend (Pranav)
- **Figma** (desktop app)
- **React DevTools** browser extension
- **Tailwind CSS IntelliSense**
- **Storybook** (once we install it)

### AI Keys (Navanish sets up shared vault — 1Password or Bitwarden free)
- Anthropic API key (Claude)
- Google AI Studio key (Gemini)
- OpenAI key (embeddings only, optional)

---

## 11. Golden Rules

These are "if you break one, the whole project suffers" rules.

1. **No work without a ticket.** Every PR links to a Linear ticket. No exceptions.
2. **No direct push to `main` or `develop`.** PR only.
3. **Every schema change is a migration.** Never edit a production DB manually. Vishal owns this.
4. **Every endpoint has an auth + RBAC check.** Default deny. Explicit allow.
5. **Every user-facing feature supports 5 roles.** Test all 5 before marking ticket done.
6. **Every query filters by `schoolId`.** Tenant leakage = project-killer. Use the tenant middleware, don't trust devs to remember.
7. **Never log PII** (passwords, tokens, full names + emails). Use structured logging.
8. **AI responses are validated.** Never show raw LLM output to users for structured data. Always parse into a schema (zod/pydantic) first.
9. **Secrets in `.env`, never in code, never in git.** Use `.env.example` to document what's needed.
10. **If a task takes > 1 day, split it.** If you're stuck > 2 hours, ask. Silence is the enemy.
11. **Write the test first if you can.** At minimum, write a test after. Untested code = broken code that hasn't been caught yet.
12. **Small PRs.** Aim for < 400 lines of diff. Huge PRs get rubber-stamped and break things.
13. **Comments explain WHY, not WHAT.** Good names make WHAT obvious.
14. **No console.log / print in main.** Use the logger. Strip debug before merge.
15. **Document every architectural decision in `docs/adr/`.** Future-you will thank you.

---

## 12. How to Add a New Feature (End-to-End Example)

Feature: **"Teacher can export a class leaderboard as PDF."**

### Step 1 — Ticket (Sprint Planning)
Create Linear ticket `SKILL-142`. Description:
> As a teacher, I want to export my class leaderboard as a PDF, so I can share it with parents during PTMs.

Acceptance criteria:
- Button on class leaderboard page: "Export PDF"
- PDF includes: school logo, class name, top 10 students, avg scores, date
- File downloads as `Leaderboard_GradeX_YYYY-MM-DD.pdf`
- Only the class's own teacher can export it (RBAC)

Estimate: 3 points. Assignee: Vishal (report), Pranav (UI).

### Step 2 — Contract first (Navanish + Vishal, 30 min)
Add to `docs/api/openapi.yaml`:
```
GET /api/v1/classes/:classId/leaderboard/export?format=pdf
Response: 200 application/pdf
```

Add to `packages/types/src/api.types.ts`:
```
export interface ExportLeaderboardParams { classId: string; format: 'pdf' | 'xlsx' }
```

### Step 3 — Branch off develop
```
git checkout develop && git pull
git checkout -b feature/SKILL-142-export-leaderboard
```

### Step 4 — Backend (Vishal)
- `report.service.ts`: add `generateLeaderboardPdf(classId)` — uses `pdfkit` or `@react-pdf/renderer`
- `report.controller.ts`: add endpoint, check `req.user.role === TEACHER`, verify class ownership
- `report.routes.ts`: wire it up
- `test/report.test.ts`: integration test that hits endpoint, asserts PDF magic bytes

### Step 5 — Frontend (Pranav, in parallel)
- Use MSW to mock the endpoint returning a dummy PDF blob
- Add "Export PDF" button to leaderboard page
- On click: fetch endpoint, trigger browser download
- When backend lands, remove mock

### Step 6 — PR
- Draft PR with title `feat(report): SKILL-142 export class leaderboard as PDF`
- CI runs: lint, typecheck, test
- Reviewers: Navanish (backend), Pranav (frontend if FE code)
- Fix review comments. Merge with Squash.

### Step 7 — Verify on staging
- Auto-deploy happens.
- Test the feature live. Move ticket to Done.

---

## 13. Security, Multi-Tenancy, Data Isolation

The proposal makes this non-negotiable. Here's how we enforce it:

### Layer 1 — Application (tenant middleware)
Every authenticated request extracts `schoolId` from the JWT. Every Prisma query is automatically scoped. Example:
- `prisma.user.findMany({ where: { schoolId: req.user.schoolId } })` — enforced by middleware wrapper.

### Layer 2 — Database (Row Level Security)
Postgres RLS policies (in `packages/db/prisma/rls-policies.sql`):
- Before every query, the API sets a session variable: `SET app.current_school = '<schoolId>'`
- Policies enforce: `USING (school_id = current_setting('app.current_school'))`
- **Even if a dev forgets the application filter, the DB refuses to return other schools' rows.**

### Layer 3 — Tests (tenant boundary tests)
A test suite that logs in as School A and tries to access School B's resources. Must get 404s on everything.

### Security checklist (Sprint 6)
- [ ] All passwords hashed with bcrypt (cost 12)
- [ ] JWT signed with rotated secret, short expiry (15 min)
- [ ] Refresh token rotation (old refresh tokens invalidated on use)
- [ ] Rate limiting: 100 req/min per user, 20/min on `/auth/*`
- [ ] CORS locked to production domain
- [ ] Helmet.js for security headers
- [ ] SQL injection: Prisma parametrizes everything ✓
- [ ] XSS: React escapes by default; sanitize user HTML on display (DOMPurify)
- [ ] CSRF: SameSite cookies or token-based (we use JWT, so mostly covered)
- [ ] File upload: validate MIME type, size limit, scan for malware (ClamAV or cloud equivalent)
- [ ] Signed URLs for private file access (expire in 1 hour)
- [ ] PII encryption at rest (Postgres TDE or column-level for sensitive fields)
- [ ] Audit log: every admin action logged with user + timestamp + IP

---

## 14. Testing Strategy

### Test pyramid
- **Lots of unit tests** (Vitest/pytest) — fast, run on every save
- **Medium integration tests** (Vitest + test DB) — run in CI
- **Few E2E tests** (Playwright) — run pre-merge, cover critical flows only:
  1. Login as each role
  2. Teacher creates quiz, student takes quiz, score saved
  3. Principal views analytics dashboard
  4. Admin onboards new school

### Coverage target
- Services (business logic): **80%**
- Utils: **90%**
- Controllers: **60%** (covered more by integration)
- UI components: **50%** (prioritize complex ones)

### AI testing
- **Snapshot tests** for prompts — prevent accidental prompt regression.
- **Evaluation harness** for AI outputs — a test set of 20 student profiles with expected career suggestions; flag if relevance drops.

---

## 15. Deployment & CI/CD

### Environments
| Env | URL | Deploys when | Database |
|---|---|---|---|
| local | `localhost` | never (dev laptops) | Docker Postgres |
| staging | `staging.skillship.com` | merge to `develop` | separate staging DB |
| production | `skillship.com` | merge to `main` (manual trigger) | prod DB |

### CI pipeline (`.github/workflows/ci.yml` — runs on every PR)
1. Checkout
2. Install pnpm, install deps (cached)
3. `pnpm lint`
4. `pnpm typecheck`
5. `pnpm test` (with test DB spun up in CI)
6. `pnpm build`
7. Python: `ruff check` + `pytest` (ai-service)
8. Upload coverage to Codecov
9. Block merge if any step fails

### CD pipeline (`.github/workflows/deploy.yml`)
- On merge to `develop` → build Docker images → push to registry → SSH deploy to staging VPS
- On merge to `main` → same but prod. Manual approval required.
- Zero-downtime deploys via `docker compose up -d` with health checks.

### Monitoring (Sprint 6 setup)
- **Sentry** — error tracking (free tier fine for us)
- **UptimeRobot** — endpoint pings every 5 min (free)
- **Log aggregation**: dump pino logs to a file, rotate daily; upgrade to Axiom/Grafana Loki later
- **Database backups**: nightly pg_dump to S3, retain 30 days

---

## 16. Definition of Done

A ticket is "Done" only when ALL of these are true:

- [ ] Code merged to `develop`
- [ ] Deployed to staging and verified working
- [ ] Unit + integration tests written and passing
- [ ] Type-safe (no `any` without justification)
- [ ] Works for all 5 roles (or explicitly scoped to fewer)
- [ ] RBAC + tenant isolation tested
- [ ] Documentation updated (OpenAPI if API, README if setup change)
- [ ] Reviewed by at least 1 teammate
- [ ] Accessibility checked (keyboard nav, screen reader labels — for UI tickets)
- [ ] Mobile responsive (for UI tickets)
- [ ] No new ESLint warnings
- [ ] Linear ticket moved to Done with PR link

---

## 17. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| AI API costs balloon | Medium | Cache results, use Gemini for bulk, monitor daily spend with alerts |
| LLM gives incorrect career advice | High | Human-review prompt outputs in Sprint 4 QA; add disclaimers; constrain outputs with schemas |
| Team member sick / unavailable | Medium | Pair programming, shared ownership of critical paths, pushed daily backups |
| Scope creep from client | High | All changes post-Sprint 1 go through written change request — per proposal |
| Tenant data leak (catastrophic) | Low prob, high impact | 3-layer defense (app + DB RLS + tests); Sprint 6 security audit |
| Deployment breaks production | Medium | Staging parity, smoke tests post-deploy, rollback playbook |
| Frontend blocked waiting for backend | High | Mock-first with MSW; OpenAPI spec before implementation |
| Performance issues at launch | Medium | Load test in Sprint 6; indexes + caching; auto-scale recommendations in proposal |

---

## Appendix A — Your First Day Checklist (new team member)

- [ ] Installed all tools from Section 10
- [ ] Cloned the repo: `git clone <url>`
- [ ] Ran `pnpm install` from root
- [ ] Copied `.env.example` → `.env` and filled in dev keys (ask Navanish)
- [ ] Started local stack: `docker compose up -d` (Postgres + Redis)
- [ ] Ran migrations: `pnpm db:migrate && pnpm db:seed`
- [ ] Ran dev: `pnpm dev`
- [ ] Opened `http://localhost:3000`, logged in as `student@test.skillship.dev` / `Test@1234`
- [ ] Read this `TEAM_PLAN.md` fully
- [ ] Skimmed the ADRs in `docs/adr/`
- [ ] Introduced yourself in `#general`
- [ ] Picked up your first ticket from the current sprint

---

## Appendix B — Glossary

- **LMS**: Learning Management System
- **Multi-tenant**: one app, many isolated customer "tenants" (schools)
- **RBAC**: Role-Based Access Control
- **RLS**: Row-Level Security (Postgres feature)
- **RAG**: Retrieval-Augmented Generation (AI pattern for grounding answers in your docs)
- **Agentic AI**: AI systems that plan and take multi-step actions autonomously
- **ADR**: Architecture Decision Record
- **BFF**: Backend-For-Frontend
- **DTO**: Data Transfer Object
- **SSR**: Server-Side Rendering
- **ORM**: Object-Relational Mapper

---

## Appendix C — "What do I do if…" FAQ

**…I need a new field on a table?**
→ Ask Vishal. He edits `schema.prisma`, runs `pnpm db:migrate dev --name add_<field>`. Update `packages/types/` accordingly. Ship in one PR.

**…I'm blocked waiting for an API?**
→ Ask backend for the OpenAPI spec entry. Mock with MSW. Build against the mock. Unblock yourself.

**…I broke staging?**
→ Revert the offending PR immediately (`gh pr revert`). Fix forward in a new PR. Tell the team in `#deploys`.

**…the client asks for a new feature mid-sprint?**
→ Do not commit in the meeting. Say: "Let me check with the team and confirm timeline by EOD." Then scope it with us and send a written change request (per payment terms).

**…I don't know how to do something?**
→ Ask in Slack within 30 min of being stuck. Don't burn 3 hours. Somebody on the team has done it before.

**…my tests are flaky?**
→ Never merge flaky tests. Fix the root cause (usually: async race, test data pollution, time dependencies). Quarantine with `test.skip` and a ticket if truly blocked.

---

**Built with rigor. Shipped with pride. Let's make Skillship the best AI LMS in India.**
