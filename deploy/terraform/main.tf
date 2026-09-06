# StudioClear — minimal Cloud Run deploy (sol.md E3.2 / E8.5).
# Deliberately narrow: a runtime service account whose ONLY privileged grant is
# reading the two API keys from Secret Manager. That secret access IS the "one
# real Cloud IAM / Workload Identity check" (sol.md §22). No broader IAM.

terraform {
  required_providers {
    google = { source = "hashicorp/google", version = "~> 5.0" }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# --- Runtime identity ---
resource "google_service_account" "runtime" {
  account_id   = "studioclear-run"
  display_name = "StudioClear Cloud Run runtime"
}

# --- Secrets (values supplied at apply time, never committed) ---
resource "google_secret_manager_secret" "parallel" {
  secret_id = "PARALLEL_API_KEY"
  replication { auto {} }
}
resource "google_secret_manager_secret_version" "parallel" {
  secret      = google_secret_manager_secret.parallel.id
  secret_data = var.parallel_api_key
}

resource "google_secret_manager_secret" "gemini" {
  secret_id = "GEMINI_API_KEY"
  replication { auto {} }
}
resource "google_secret_manager_secret_version" "gemini" {
  secret      = google_secret_manager_secret.gemini.id
  secret_data = var.gemini_api_key
}

# --- The one real IAM check: SA may read exactly these two secrets ---
resource "google_secret_manager_secret_iam_member" "parallel_access" {
  secret_id = google_secret_manager_secret.parallel.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}
resource "google_secret_manager_secret_iam_member" "gemini_access" {
  secret_id = google_secret_manager_secret.gemini.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

# --- Service ---
resource "google_cloud_run_v2_service" "studioclear" {
  name     = "studioclear"
  location = var.region

  template {
    service_account = google_service_account.runtime.email
    containers {
      image = var.image
      ports { container_port = 8080 }

      env {
        name = "PARALLEL_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.parallel.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini.secret_id
            version = "latest"
          }
        }
      }
    }
  }
}

# Public demo access (drop for a private deployment).
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.studioclear.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "url" {
  value = google_cloud_run_v2_service.studioclear.uri
}
