"""Tamper-evident audit log (sol.md E8.3): the hash chain detects any edit."""

from studioclear.security.audit import GENESIS, AuditLog


def test_chain_verifies_when_intact():
    log = AuditLog()
    log.append({"action": "script_uploaded"})
    log.append({"action": "tool_denied", "tool": "unapproved_legal_database"})
    log.append({"action": "report_generated"})
    assert log.verify()
    assert log.events[0].prev_hash == GENESIS


def test_tampering_breaks_verification():
    log = AuditLog()
    log.append({"action": "tool_denied", "decision": "DENY"})
    log.append({"action": "report_generated"})
    # Someone edits history to hide the denial.
    log.events[0].body["decision"] = "ALLOW"
    assert not log.verify()


def test_deletion_breaks_verification():
    log = AuditLog()
    log.append({"action": "a"})
    log.append({"action": "b"})
    del log.events[0]
    assert not log.verify()
