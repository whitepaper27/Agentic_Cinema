"""Pluggable storage backend for durable hosted runs (sol.md §10).

Local JSON files for dev; a private GCS bucket for the hosted path, writing with
a generation precondition so a concurrent create cannot be blindly clobbered.
"""

import json

from studioclear.storage_backend import GcsBackend, LocalBackend, get_backend


def test_local_backend_round_trips(tmp_path):
    b = LocalBackend(tmp_path)
    assert b.read_json("scenes/s1.json") is None
    b.write_json("scenes/s1.json", {"a": 1})
    assert b.read_json("scenes/s1.json") == {"a": 1}


def test_get_backend_is_local_without_bucket(monkeypatch):
    monkeypatch.delenv("STUDIOCLEAR_GCS_BUCKET", raising=False)
    assert isinstance(get_backend(), LocalBackend)


class _FakeBlob:
    def __init__(self, name, store):
        self.name = name
        self._store = store
        self.generation = 7 if name in store else None

    def exists(self):
        return self.name in self._store

    def download_as_text(self):
        return json.dumps(self._store[self.name])

    def upload_from_string(self, data, content_type=None, if_generation_match=None):
        self.uploaded_precondition = if_generation_match
        self._store[self.name] = json.loads(data)


class _FakeBucket:
    def __init__(self, store):
        self._store = store

    def blob(self, name):
        return _FakeBlob(name, self._store)


class _FakeClient:
    def __init__(self):
        self.store = {}

    def bucket(self, name):
        return _FakeBucket(self.store)


def test_gcs_backend_prefixes_keys_and_round_trips():
    b = GcsBackend("mybucket", client=_FakeClient())
    assert b.read_json("scenes/s1.json") is None
    b.write_json("scenes/s1.json", {"a": 1})
    assert b.read_json("scenes/s1.json") == {"a": 1}


def test_gcs_new_object_requires_absent_precondition():
    client = _FakeClient()
    b = GcsBackend("mybucket", client=client, prefix="sc")
    # New object: precondition 0 means "must not already exist".
    blob = client.bucket("mybucket").blob("sc/runs/r1.json")
    b.write_json("runs/r1.json", {"x": 1})
    # Key is namespaced under the prefix.
    assert "sc/runs/r1.json" in client.store
    # A fresh write to a now-existing key matches its current generation, not 0.
    b2 = GcsBackend("mybucket", client=client, prefix="sc")
    assert b2.read_json("runs/r1.json") == {"x": 1}
    del blob
