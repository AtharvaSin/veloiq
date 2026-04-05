"""Seed 10 match_results + 10 assessments + 8 notifications + 3 sales_escalations."""
import hashlib
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard

# ---------------------------------------------------------------------------
# Curated match_results
# (cert_link_idx, standard_idx, sim, lev, jw, ts, confidence_tier, status)
# All indices reference the CURATED_LINKS / CURATED_STANDARDS lists from the
# certificate seeder (0-based).
# ---------------------------------------------------------------------------
CURATED_MATCHES: list[dict[str, Any]] = [
    # Auto-matches (similarity > 0.95)
    {"link": 7,  "std": 2, "sim": "0.998", "lev": "0.995", "jw": "0.999", "ts": "1.000", "tier": "auto_match",    "status": "reviewed"},  # clean ISO 45001
    {"link": 13, "std": 2, "sim": "0.998", "lev": "0.995", "jw": "0.999", "ts": "1.000", "tier": "auto_match",    "status": "reviewed"},  # clean ISO 45001 (Mahindra)
    {"link": 14, "std": 5, "sim": "0.996", "lev": "0.993", "jw": "0.998", "ts": "1.000", "tier": "auto_match",    "status": "reviewed"},  # clean ISO 13485
    {"link": 1,  "std": 0, "sim": "0.972", "lev": "0.940", "jw": "0.985", "ts": "0.960", "tier": "auto_match",    "status": "reviewed"},  # fuzzy DIN EN ISO 9001
    {"link": 2,  "std": 3, "sim": "0.958", "lev": "0.920", "jw": "0.972", "ts": "0.945", "tier": "auto_match",    "status": "reviewed"},  # fuzzy EN IEC 62368
    # Expert review (0.70-0.95)
    {"link": 3,  "std": 1, "sim": "0.892", "lev": "0.855", "jw": "0.910", "ts": "0.880", "tier": "expert_review", "status": "reviewed"},  # BS EN ISO 14001
    {"link": 0,  "std": 9, "sim": "0.842", "lev": "0.780", "jw": "0.870", "ts": "0.830", "tier": "expert_review", "status": "reviewed"},  # DIN EN 62443 VDE prefix
    {"link": 4,  "std": 6, "sim": "0.810", "lev": "0.755", "jw": "0.832", "ts": "0.810", "tier": "expert_review", "status": "pending"},   # IEC 60601-1 Ed.3.2 — STILL OPEN
    # Manual triage (< 0.70)
    {"link": 6,  "std": 4, "sim": "0.680", "lev": "0.620", "jw": "0.705", "ts": "0.680", "tier": "manual_triage", "status": "reviewed"},  # IEC 61010-1 cross-match
    {"link": 11, "std": 1, "sim": "0.540", "lev": "0.480", "jw": "0.560", "ts": "0.590", "tier": "manual_triage", "status": "reviewed"},  # ISO 14001 low-quality
]

# ---------------------------------------------------------------------------
# Curated assessments — realistic TIC compliance reasoning
# (match_idx, assessor, impact, action, reason_code, notes, decision, decided_offset_days)
# ---------------------------------------------------------------------------
CURATED_ASSESSMENTS: list[dict[str, Any]] = [
    {
        "match": 0, "assessor": "Dr. M. Weber",   "impact": "no_change",       "action": "reconfirm",
        "rc": "RC-NC-2015-A",
        "notes": "ISO 45001 linkage confirmed. Certificate recertification not triggered — current cert already covers 2018 revision.",
        "decision": "approved",   "days": -12,
    },
    {
        "match": 1, "assessor": "Dr. M. Weber",   "impact": "no_change",       "action": "reconfirm",
        "rc": "RC-NC-2015-B",
        "notes": "ISO 45001 duplicate reference confirmed for Tata Steel OHS cert. No procedural changes required.",
        "decision": "approved",   "days": -8,
    },
    {
        "match": 2, "assessor": "Dr. S. Chen",    "impact": "no_change",       "action": "reconfirm",
        "rc": "RC-NC-2016-C",
        "notes": "ISO 13485:2016 remains valid for Rolls-Royce medical device cert. Linked correctly; no action required.",
        "decision": "approved",   "days": -25,
    },
    {
        "match": 3, "assessor": "Dr. M. Weber",   "impact": "administrative",  "action": "reconfirm",
        "rc": "RC-AD-9001-A",
        "notes": "DIN EN ISO 9001:2015-11 is the DIN harmonized adoption of ISO 9001:2015. Editorial prefix only — identical clause text. Customer reconfirmation sufficient.",
        "decision": "approved",   "days": -5,
    },
    {
        "match": 4, "assessor": "Dr. S. Chen",    "impact": "administrative",  "action": "reconfirm",
        "rc": "RC-AD-2368-A",
        "notes": "EN IEC 62368-1:2023/AC:2024 is the CENELEC corrigendum to IEC 62368-1:2023. Fixes typographical errors in Annex F. No impact on Huawei 5G BBU certification.",
        "decision": "approved",   "days": -7,
    },
    {
        "match": 5, "assessor": "Dr. R. Kumar",   "impact": "minor_technical", "action": "reconfirm",
        "rc": "RC-MN-14001-B",
        "notes": "BS EN ISO 14001:2015 clause 6.1.2 has been clarified by BSI with additional guidance on compliance obligations. Hitachi to reconfirm updated environmental aspects register — no change to certificate.",
        "decision": "approved",   "days": -18,
    },
    {
        "match": 6, "assessor": "Dr. A. Müller",  "impact": "minor_technical", "action": "retest",
        "rc": "RC-MN-62443-A",
        "notes": "DIN EN 62443-3-3 VDE 0802-3-3:2023-12 introduces stricter SL-T (security level target) verification for Siemens PLC. Customer must submit updated security requirements specification; lab retest for SR 1.1/1.2 required.",
        "decision": "approved",   "days": -3,
    },
    {
        "match": 7, "assessor": "Dr. A. Müller",  "impact": "major_technical", "action": "retest",
        "rc": "RC-MJ-60601-A",
        "notes": "IEC 60601-1 Ed.3.2:2020 introduces new essential performance requirements (Clause 4.3) and requires updated risk management file per ISO 14971:2019. Rolls-Royce EECU medical electrical cert must retest — full Ed.3.2 type test campaign required.",
        "decision": "escalated",  "days": -1,
    },
    {
        "match": 8, "assessor": "Dr. L. Schmidt", "impact": "safety_critical", "action": "suspend",
        "rc": "RC-SC-61010-A",
        "notes": "Spurious match — IEC 61010-1:2010 does not apply to Honeywell gas detector product category. Flagged for manual triage review; do not use this match for notification dispatch.",
        "decision": "rejected",   "days": -40,
    },
    {
        "match": 9, "assessor": "Dr. L. Schmidt", "impact": "no_change",       "action": "reconfirm",
        "rc": "RC-NC-14001-C",
        "notes": "Low-confidence candidate link rejected. ISO 14001:2015 is not referenced in Honeywell BW Solo product cert; manual triage confirms no match.",
        "decision": "rejected",   "days": -32,
    },
]

# ---------------------------------------------------------------------------
# Curated notifications
# Only assessments with decision="approved" and action in {reconfirm, retest}
# generate notifications → assessments 0-7 → 8 notifications.
# (assessment_idx, status, sla_days_from_now)
# ---------------------------------------------------------------------------
CURATED_NOTIFICATIONS: list[dict[str, Any]] = [
    {"assess": 0, "status": "delivered", "sla_days": 90},
    {"assess": 1, "status": "opened",    "sla_days": 80},
    {"assess": 2, "status": "clicked",   "sla_days": 120},
    {"assess": 3, "status": "delivered", "sla_days": 60},
    {"assess": 4, "status": "opened",    "sla_days": 45},
    {"assess": 5, "status": "clicked",   "sla_days": 90},
    {"assess": 6, "status": "breached",  "sla_days": -5},    # overdue — escalation trigger
    {"assess": 7, "status": "breached",  "sla_days": -12},   # overdue — escalation trigger
]

# ---------------------------------------------------------------------------
# Curated sales escalations
# (notif_idx, reason, opportunity_value, assigned_to, status, resolved_offset_days|None)
# ---------------------------------------------------------------------------
CURATED_ESCALATIONS: list[dict[str, Any]] = [
    {"notif": 6, "reason": "retest_overdue",      "value": "85000.00",  "assigned": "Markus Hoffmann",  "status": "open",      "resolved_days": None},
    {"notif": 7, "reason": "major_change_retest", "value": "450000.00", "assigned": "Jennifer Walsh",   "status": "contacted", "resolved_days": None},
    {"notif": 0, "reason": "sla_breach",          "value": "125000.00", "assigned": "Priya Kapoor",     "status": "resolved",  "resolved_days": -2},
]


# ---------------------------------------------------------------------------
# Notification content helpers
# ---------------------------------------------------------------------------

def _notification_subject(action: str, standard_ac: str) -> str:
    """Build a branded TÜV Rheinland notification subject line."""
    action_verb_map = {
        "reconfirm": "confirmation required",
        "retest":    "retest required",
        "suspend":   "suspension notice",
        "withdraw":  "withdrawal notice",
    }
    verb = action_verb_map.get(action, "action required")
    return f"TÜV Rheinland — {standard_ac}: {verb}"


def _notification_body(customer_company: str, standard_ac: str, assessment: dict[str, Any]) -> str:
    """Build a branded TÜV Rheinland HTML notification body."""
    impact_readable = assessment["impact"].replace("_", " ")
    return (
        f"<p>Dear {customer_company},</p>"
        f"<p>TÜV Rheinland has completed the impact assessment for <strong>{standard_ac}</strong>. "
        f"Our expert review ({assessment['assessor']}) found: {impact_readable}.</p>"
        f"<p><strong>Action required:</strong> {assessment['action']}</p>"
        f"<p><strong>Reason code:</strong> {assessment['rc']}</p>"
        f"<p><strong>Review notes:</strong> {assessment['notes']}</p>"
        f"<p>Please respond within the SLA window. Contact your TÜV account manager for questions.</p>"
        f"<p>— TÜV Rheinland Standards Automation Platform</p>"
    )


# ---------------------------------------------------------------------------
# Seeder
# ---------------------------------------------------------------------------

def seed_historical(
    db: Session,
    standards: list[Standard],
    cert_links: list[CertStandardLink],
    customers: list[Customer],
    fake: object | None = None,
) -> tuple[list[MatchResult], list[Assessment], list[Notification], list[SalesEscalation]]:
    """Seed curated historical match_results, assessments, notifications, escalations.

    The ``fake`` parameter is accepted but unused — data is fully curated.
    """
    from app.models.certificate import Certificate  # local import to avoid circular

    now = datetime.now(UTC)

    # -----------------------------------------------------------------------
    # 10 match_results
    # -----------------------------------------------------------------------
    matches: list[MatchResult] = []
    for row in CURATED_MATCHES:
        link = cert_links[row["link"]]
        std = standards[row["std"]]
        status = row["status"]
        reviewed_at = now - timedelta(days=5) if status == "reviewed" else None
        matched_at = (reviewed_at or now) - timedelta(hours=24)

        match = MatchResult(
            natos_standard_id=std.id,
            cert_link_id=link.id,
            similarity_score=Decimal(row["sim"]),
            levenshtein_score=Decimal(row["lev"]),
            jaro_winkler_score=Decimal(row["jw"]),
            token_set_score=Decimal(row["ts"]),
            confidence_tier=row["tier"],
            status=status,
            matched_at=matched_at,
            reviewed_at=reviewed_at,
        )
        db.add(match)
        matches.append(match)

    db.flush()

    # -----------------------------------------------------------------------
    # 10 assessments
    # -----------------------------------------------------------------------
    assessments: list[Assessment] = []
    for row in CURATED_ASSESSMENTS:
        match = matches[row["match"]]
        decided_at = now + timedelta(days=row["days"])  # days are negative → past

        sig_input = f"{match.id}:{row['assessor']}:{decided_at.isoformat()}".encode()
        signature = hashlib.sha256(sig_input).hexdigest()

        assessment = Assessment(
            match_result_id=match.id,
            assessor_id=row["assessor"],
            impact_classification=row["impact"],
            action_required=row["action"],
            reason_code=row["rc"],
            notes=row["notes"],
            decision=row["decision"],
            decided_at=decided_at,
            signature_hash=signature,
        )
        db.add(assessment)
        assessments.append(assessment)

    db.flush()

    # -----------------------------------------------------------------------
    # 8 notifications
    # Build reverse-lookup maps: link → certificate → customer
    # -----------------------------------------------------------------------
    cert_id_to_customer: dict[UUID, UUID] = {}
    cert_ids = {lnk.certificate_id for lnk in cert_links}
    for cert in db.query(Certificate).filter(Certificate.id.in_(cert_ids)).all():
        cert_id_to_customer[cert.id] = cert.customer_id

    customer_by_id: dict[UUID, Customer] = {c.id: c for c in customers}
    link_by_id: dict[UUID, CertStandardLink] = {lnk.id: lnk for lnk in cert_links}

    notifications: list[Notification] = []
    for row in CURATED_NOTIFICATIONS:
        assessment = assessments[row["assess"]]
        match = next(m for m in matches if m.id == assessment.match_result_id)
        link = link_by_id[match.cert_link_id]
        customer_id = cert_id_to_customer[link.certificate_id]
        customer = customer_by_id[customer_id]
        standard = next(s for s in standards if s.id == match.natos_standard_id)

        status = row["status"]
        sla_days = row["sla_days"]
        # sla_deadline is relative to now
        sla_deadline = now + timedelta(days=sla_days)
        # sent_at is 5 days before deadline for normal, or some time before it
        sent_at = sla_deadline - timedelta(days=14)

        delivered_at = (
            sent_at + timedelta(minutes=10)
            if status in {"delivered", "opened", "clicked", "breached"}
            else None
        )
        opened_at = (
            (delivered_at + timedelta(hours=2)) if status in {"opened", "clicked"} and delivered_at else None
        )
        clicked_at = (
            (opened_at + timedelta(minutes=30)) if status == "clicked" and opened_at else None
        )

        subject = _notification_subject(assessment.action_required, standard.ac_code)
        body = _notification_body(customer.company_name, standard.ac_code, CURATED_ASSESSMENTS[row["assess"]])

        notification = Notification(
            assessment_id=assessment.id,
            customer_id=customer_id,
            template_language=customer.language,
            subject=subject,
            body_html=body,
            status=status,
            sent_at=sent_at,
            delivered_at=delivered_at,
            opened_at=opened_at,
            clicked_at=clicked_at,
            sla_deadline=sla_deadline,
        )
        db.add(notification)
        notifications.append(notification)

    db.flush()

    # -----------------------------------------------------------------------
    # 3 sales escalations
    # -----------------------------------------------------------------------
    escalations: list[SalesEscalation] = []
    for row in CURATED_ESCALATIONS:
        notification = notifications[row["notif"]]
        resolved_at = (now + timedelta(days=row["resolved_days"])) if row["resolved_days"] is not None else None

        escalation = SalesEscalation(
            notification_id=notification.id,
            customer_id=notification.customer_id,
            escalation_reason=row["reason"],
            opportunity_value=Decimal(row["value"]),
            assigned_to=row["assigned"],
            status=row["status"],
            created_at=notification.sla_deadline + timedelta(hours=1),
            resolved_at=resolved_at,
        )
        db.add(escalation)
        escalations.append(escalation)

    db.flush()
    return matches, assessments, notifications, escalations
