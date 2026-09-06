# Deploying StudioClear to Cloud Run

Three paths. **Option A needs no local tooling** (no Docker, no gcloud) — use it
since the repo is already public on GitHub. Nothing here is applied
automatically.

Prereqs regardless: a GCP project with billing, and the two API keys.

---

## Option A — Deploy from GitHub via the Cloud Console (recommended, no local tools)

1. Push secrets (once), in **Secret Manager** → *Create secret*:
   - `PARALLEL_API_KEY` = your Parallel key
   - `GEMINI_API_KEY` = your Gemini key
2. **Cloud Run** → *Deploy container* → **Continuously deploy from a repository**
   → *Set up with Cloud Build* → connect `whitepaper27/Agentic_Cinema`, branch
   `main`, **Build type: Dockerfile**.
3. In the service settings:
   - **Region** us-central1, **Allow unauthenticated** (public demo).
   - **Variables & Secrets** → *Reference a secret* → expose
     `PARALLEL_API_KEY` and `GEMINI_API_KEY` as env vars (latest version).
4. Deploy. Cloud Build builds the `Dockerfile` and Cloud Run gives you a URL.
   Every push to `main` redeploys.

That's it — the app reads the keys from those env vars (`studioclear/config.py`),
and writes run data under `/tmp` (set by the Dockerfile).

---

## Option B — one command (requires gcloud installed + `gcloud auth login`)

Install the Google Cloud SDK first (https://cloud.google.com/sdk/docs/install),
then:

```bash
gcloud config set project <PROJECT_ID>
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com

printf '%s' "$PARALLEL_API_KEY" | gcloud secrets create PARALLEL_API_KEY --data-file=-
printf '%s' "$GEMINI_API_KEY"   | gcloud secrets create GEMINI_API_KEY   --data-file=-

gcloud run deploy studioclear \
  --source . --region us-central1 --allow-unauthenticated \
  --set-secrets PARALLEL_API_KEY=PARALLEL_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest
```

---

## Option C — Terraform (reproducible, requires gcloud + terraform)

```bash
cd deploy/terraform
terraform init
terraform apply \
  -var project_id=<PROJECT_ID> \
  -var image=us-central1-docker.pkg.dev/<PROJECT_ID>/studioclear/app:latest \
  -var parallel_api_key=$PARALLEL_API_KEY \
  -var gemini_api_key=$GEMINI_API_KEY
```

Provisions a dedicated runtime service account whose only privileged grant is
`secretAccessor` on the two API-key secrets — that Secret Manager read is
StudioClear's one genuine Cloud IAM check (sol.md §22 / E8.5).

---

## Notes

- Keys are read from env; never baked into the image or committed.
- Run data is written under `/tmp/studioclear` (ephemeral) — fine for the demo;
  swap the store to Firestore for persistence (sol.md §11).
- For Vertex AI instead of the Gemini Developer API, set
  `GOOGLE_GENAI_USE_VERTEXAI=true` and grant the SA `roles/aiplatform.user`.
- **Agentic (ADK) mode is slower** (one agent run per item) — the UI defaults to
  the fast path; toggle "Agentic (ADK)" to demo the ADK researcher live.
