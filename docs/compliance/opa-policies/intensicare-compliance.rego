# OPA/Rego Compliance Policies — IntensiCare
# Regulatory: LGPD (Brazil), ANS RN 277, CFM Resolution 1.821/2007
# Version: 1.0.0 — initial policy set

package intensicare.compliance

# ─────────────────────────────────────────────────────────────
# POLICY 1: PHI Encryption at Rest (LGPD Art. 46)
# ─────────────────────────────────────────────────────────────

default allow_phi_storage = false

allow_phi_storage {
    input.resource.storage_encrypted == true
    input.resource.encryption_key_managed == true
}

violation_phi_unencrypted[msg] {
    resource := input.resources[_]
    resource.type == "database"
    resource.contains_phi == true
    not resource.storage_encrypted
    msg := sprintf("PHI data store '%s' requires encryption at rest (LGPD Art. 46)", [resource.name])
}

# ─────────────────────────────────────────────────────────────
# POLICY 2: Audit Trail Immutability (CFM 1.821/2007)
# ─────────────────────────────────────────────────────────────

violation_audit_mutable[msg] {
    resource := input.resources[_]
    resource.type == "audit_log"
    resource.append_only == false
    msg := sprintf("Audit log '%s' must be append-only (CFM 1.821/2007)", [resource.name])
}

# ─────────────────────────────────────────────────────────────
# POLICY 3: Clinical Data Minimum Retention (CFM 1.821/2007)
# ─────────────────────────────────────────────────────────────

violation_short_retention[msg] {
    resource := input.resources[_]
    resource.type == "clinical_record"
    resource.retention_days < 7300  # 20 years
    msg := sprintf("Clinical record '%s' retention is %d days (minimum 7300 days / 20 years per CFM 1.821/2007)", [resource.name, resource.retention_days])
}

# ─────────────────────────────────────────────────────────────
# POLICY 4: LGPD Erasure Cascade (LGPD Art. 18)
# ─────────────────────────────────────────────────────────────

default allow_erasure = false

allow_erasure {
    input.erasure_request.verified == true
    input.erasure_request.scope == "all_tables"
    input.erasure_request.audit_logged == true
}

# ─────────────────────────────────────────────────────────────
# POLICY 5: Authentication — MFA for Admin Access (ANS RN 277)
# ─────────────────────────────────────────────────────────────

violation_admin_no_mfa[msg] {
    user := input.users[_]
    user.role == "admin"
    not user.mfa_enabled
    msg := sprintf("Admin user '%s' requires MFA (ANS RN 277)", [user.username])
}

# ─────────────────────────────────────────────────────────────
# POLICY 6: Data Isolation per Tenant (Multi-tenancy)
# ─────────────────────────────────────────────────────────────

violation_cross_tenant_access[msg] {
    query := input.queries[_]
    query.tenant_id != input.context.tenant_id
    not input.context.is_admin
    msg := sprintf("Cross-tenant access denied: query from tenant '%s' attempted access to tenant '%s'", [input.context.tenant_id, query.tenant_id])
}

# ─────────────────────────────────────────────────────────────
# POLICY 7: Security Headers (OWASP)
# ─────────────────────────────────────────────────────────────

violation_missing_headers[msg] {
    endpoint := input.endpoints[_]
    required_headers := {"content-security-policy", "x-frame-options", "strict-transport-security"}
    missing := {h | h := required_headers[_]; not endpoint.response_headers[h]}
    count(missing) > 0
    msg := sprintf("Endpoint '%s' missing security headers: %s", [endpoint.path, concat(", ", missing)])
}
