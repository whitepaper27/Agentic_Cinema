# Deploying StudioClear to Cloud Run

Scaffolding only — run when you're ready (sol.md Day-4). Nothing here is applied
automatically. Two paths: quick `gcloud`, or reproducible Terraform.

## Prereqs (once)

```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com aiplatform.googleapis.com
```

## Option A — quick deploy (source-based)

```bash
# From repo root. Cloud Run builds the Dockerfile for you.
gcloud run deploy studioclear \
  --source . --region us-central1 --allow-unauthenticated \
  --set-secrets PARALLEL_API_KEY=PARALLEL_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest
```

(Create the secrets first: `printf '%s' "$KEY" | gcloud secrets create PARALLEL_API_KEY --data-file=-`.)

## Option B — Terraform (reproducible)

```bash
cd deploy/terraform
terraform init
terraform apply \
  -var project_id=<PROJECT_ID> \
  -var image=us-central1-docker.pkg.dev/<PROJECT_ID>/studioclear/app:latest \
  -var parallel_api_key=$PARALLEL_API_KEY \
  -var gemini_api_key=$GEMINI_API_KEY
# outputs the service URL
```

Terraform provisions a dedicated runtime service account whose only privileged
grant is `secretAccessor` on the two API-key secrets — that Secret Manager read
is StudioClear's one genuine Cloud IAM check (sol.md §22 / E8.5). Everything else
is deliberately out of scope for the hackathon timeline.

## Notes

- The container reads keys from env; Cloud Run injects them from Secret Manager
  via the service account (no keys in the image or repo).
- For Vertex AI instead of the Gemini Developer API, set
  `GOOGLE_GENAI_USE_VERTEXAI=true` and grant the SA `roles/aiplatform.user`.
