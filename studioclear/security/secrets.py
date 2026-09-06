"""Secret access — the one real Cloud IAM / Workload Identity check (sol.md E3.2 / E8.5).

Locally: read PARALLEL_API_KEY from the environment (.env).
On Cloud Run: read it from Secret Manager using the service account. That
Secret Manager access IS the genuine IAM check — nothing broader is built
(sol.md keeps this narrow to avoid the 4-day scope-blowup trap).
"""

from __future__ import annotations

import os

# STUB: swap to Secret Manager when deploying (E3.2). Kept minimal on purpose.
#   from google.cloud import secretmanager
#   client = secretmanager.SecretManagerServiceClient()
#   name = f"projects/{project}/secrets/PARALLEL_API_KEY/versions/latest"
#   return client.access_secret_version(name=name).payload.data.decode()


def get_parallel_api_key() -> str | None:
    return os.getenv("PARALLEL_API_KEY")
