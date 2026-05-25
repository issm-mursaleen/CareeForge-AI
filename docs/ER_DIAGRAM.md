# Entity Relationship — CareerForge AI

MongoDB is document-oriented, so this is a logical ER, not a relational schema. Refs (`user_id`, etc.) are stored as `ObjectId` and resolved via service-layer lookups.

```
┌─────────────────────────┐
│         User            │
│─────────────────────────│
│ _id            ObjectId │◄────────────────────────────┐
│ email          string   │                              │
│ password_hash  string   │                              │
│ full_name      string   │                              │
│ role           enum     │                              │
│ created_at     datetime │                              │
│ profile        object   │                              │
└────────┬────────────────┘                              │
         │1                                              │1
         │                                               │
         │N                                              │N
┌────────▼────────────────┐  ┌──────────────────────────┴────────┐
│        Resume           │  │           JobMatch                 │
│─────────────────────────│  │────────────────────────────────────│
│ _id            ObjectId │  │ _id                ObjectId        │
│ user_id        ref→User │  │ recruiter_id       ref→User        │
│ file_name      string   │  │ job_description    string          │
│ file_url       string   │  │ resume_ids         ref[]→Resume    │
│ raw_text       string   │  │ algorithms         enum[]          │
│ processed      object   │  │ scores             object          │
│ ats_score      number   │  │ llm_explanations   object[]        │
│ skills         string[] │  │ created_at         datetime        │
│ missing_skills string[] │  └────────────────────────────────────┘
│ weak_sections  string[] │
│ category       string   │
│ created_at     datetime │
└────────┬────────────────┘
         │1
         │
         │N
┌────────▼────────────────┐  ┌───────────────────────────────────┐
│       Interview         │  │           Roadmap                  │
│─────────────────────────│  │────────────────────────────────────│
│ _id            ObjectId │  │ _id                ObjectId        │
│ user_id        ref→User │  │ user_id            ref→User        │
│ resume_id      ref→Res  │  │ target_role        string          │
│ role           string   │  │ milestones         object[]        │
│ questions      object[] │  │ skill_gaps         string[]        │
│ answers        object[] │  │ recommended_resources object[]     │
│ score          number   │  │ created_at         datetime        │
│ feedback       string   │  │ updated_at         datetime        │
│ created_at     datetime │  └───────────────────────────────────┘
└─────────────────────────┘

┌─────────────────────────┐  ┌───────────────────────────────────┐
│       ChatHistory       │  │           Analytics                │
│─────────────────────────│  │────────────────────────────────────│
│ _id            ObjectId │  │ _id                ObjectId        │
│ user_id        ref→User │  │ user_id            ref→User        │
│ session_id     string   │  │ date               date            │
│ messages       object[] │  │ resumes_analyzed   number          │
│   role: user|ai         │  │ rankings_run       number          │
│   content: string       │  │ interviews_taken   number          │
│   ts: datetime          │  │ chat_messages      number          │
│ created_at     datetime │  │ ats_score_avg      number          │
└─────────────────────────┘  └───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          AILog                                   │
│──────────────────────────────────────────────────────────────────│
│ _id             ObjectId    user_id      ref→User                │
│ feature         string      model        string  (groq/gemini)   │
│ tokens_in       number      tokens_out   number                  │
│ latency_ms      number      cost_usd     number                  │
│ created_at      datetime                                         │
└──────────────────────────────────────────────────────────────────┘
```

## Index strategy

```
users.email            unique
users.role             non-unique
resumes.user_id+created_at  compound, descending
job_matches.recruiter_id+created_at  compound, descending
interviews.user_id     non-unique
analytics.user_id+date unique compound
ai_logs.created_at     non-unique, TTL 90 days (auto-prune)
chat_history.user_id+session_id  compound
roadmaps.user_id       non-unique
```
