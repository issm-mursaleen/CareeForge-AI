# CareerForge AI — REST API

Base URL: `/api/v1`. All authenticated endpoints require `Authorization: Bearer <access_token>`.

Live OpenAPI/Swagger UI: `http://localhost:8000/docs`

## Conventions

- Request/response bodies are JSON unless explicitly multipart.
- Errors follow the shape:
  ```json
  { "code": "validation_failed", "message": "...", "details": null }
  ```
- Times are ISO-8601 UTC.

## Auth

### `POST /auth/register`
Create an account and return a token pair.

Body: `{ email, password, full_name, role? }` — role ∈ `user|recruiter|admin` (admin can't be self-assigned in prod; gate via seed).

Returns: `{ access_token, refresh_token, token_type }`

### `POST /auth/login`
Body: `{ email, password }` → `TokenPair`.

### `POST /auth/refresh`
Body: `{ refresh_token }` → new `TokenPair`.

### `GET /auth/me`
Returns the authenticated user.

## Resumes

### `POST /resumes/analyze` *(multipart)*
Fields: `file` (PDF/DOCX/TXT, ≤ 5 MB), `job_description` (optional).

Returns: `ResumeAnalysis` with ATS breakdown, detected skills, missing skills vs JD, quality notes.

### `GET /resumes`
List all of the caller's resumes.

### `GET /resumes/{resume_id}`
Full detail + raw text preview.

## Ranking

### `POST /ranking`
Body:
```json
{
  "job_title": "Senior ML Engineer",
  "job_description": "...",
  "resume_ids": ["6720...", "6720..."],
  "algorithms": ["bm25", "bert"],
  "explain_top_k": 3
}
```

Returns `RankingResponse` with ranked candidates, per-algorithm scores, composite, and LLM Good/Bad Fit explanations for the top K.

## Interview

### `POST /interview/generate`
Body: `{ role, resume_id, count }` → interview with N questions.

### `POST /interview/{interview_id}/answer`
Body: `{ question_index, answer }` → `{ score, feedback, strengths, improvements }`.

## Roadmap

### `POST /roadmap`
Body: `{ target_role, resume_id }` → roadmap with skill gaps, 12-week milestones, curated resources.

### `GET /roadmap`
List all roadmaps for the caller.

## Chat

### `POST /chat`
Body: `{ session_id?, message }` → `{ session_id, reply }`. Pass back the `session_id` to maintain context.

## Analytics

### `GET /analytics/summary`
Returns `{ total_resumes, average_ats, top_skills, ats_trend }` for the caller.

## Admin (admin role only)

### `GET /admin/overview`
Platform totals + per-role user breakdown + AI cost.

### `GET /admin/users?limit=50`
List users.

## Status codes

| Code | Meaning |
|------|---------|
| 200 / 201 | success |
| 401 | missing or invalid token |
| 403 | wrong role |
| 404 | resource not found |
| 409 | conflict (e.g., email already exists) |
| 422 | validation failed (pydantic) |
| 502 | external service (Gemini / Groq) failed |
