"""StudioClear security layer (sol.md §15–§17, E8).

- tool_registry: the approved-capability allow-list
- authorization: StudioClear AuthZ decision (real DENY, E3.2/§17)
- audit: tamper-evident hash-chained audit log (E8.3)
- secrets: Secret Manager read = the one real IAM check (E3.2, stub)
"""
