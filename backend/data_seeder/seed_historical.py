"""Seed 30 match_results + 30 assessments + 20 notifications + 5 sales_escalations."""
import hashlib
import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from faker import Faker
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard

MATCH_TIER_DISTRIBUTION: list[tuple[str, int, tuple[float, float]]] = [
    # (confidence_tier, count, (score_min, score_max))
    ("auto_match", 10, (0.951, 0.999)),
    ("expert_review", 15, (0.700, 0.950)),
    ("manual_triage", 5, (0.400, 0.699)),
]

ASSESSMENT_IMPACT_DISTRIBUTION: list[tuple[str, int]] = [
    ("no_change", 10),
    ("minor_technical", 10),
    ("major_technical", 5),
    ("safety_critical", 5),
]

IMPACT_TO_ACTION: dict[str, str] = {
    "no_change": "reconfirm",
    "administrative": "reconfirm",
    "minor_technical": "reconfirm",
    "major_technical": "retest",
    "safety_critical": "suspend",
}

NOTIFICATION_STATUS_MIX: list[tuple[str, int]] = [
    # Total = 20; 5 breached drives the 5 escalations
    ("sent", 3),
    ("delivered", 3),
    ("opened", 4),
    ("clicked", 5),
    ("breached", 5),
]

ASSESSORS = (
    "Dr. M. Weber", "Dr. S. Chen", "Dr. R. Kumar", "Dr. A. Müller", "Dr. L. Schmidt",
)


def _round(value: float) -> Decimal:
    return Decimal(f"{value:.3f}")


def seed_historical(
    db: Session,
    standards: list[Standard],
    cert_links: list[CertStandardLink],
    customers: list[Customer],
) -> tuple[list[MatchResult], list[Assessment], list[Notification], list[SalesEscalation]]:
    """Seed historical match_results, assessments, notifications, sales_escalations."""
    fake = Faker()
    now = datetime.now(UTC)

    # --- 30 match_results ---
    matches: list[MatchResult] = []
    used_pairs: set[tuple[UUID, UUID]] = set()
    link_pool = list(cert_links)
    random.shuffle(link_pool)
    link_idx = 0

    for tier, count, (score_min, score_max) in MATCH_TIER_DISTRIBUTION:
        for _ in range(count):
            # Pick a unique (standard, link) pair
            while True:
                std = random.choice(standards)
                link = link_pool[link_idx % len(link_pool)]
                link_idx += 1
                pair = (std.id, link.id)
                if pair not in used_pairs:
                    used_pairs.add(pair)
                    break

            score = random.uniform(score_min, score_max)
            lev = random.uniform(score_min - 0.05, min(score_max + 0.02, 1.0))
            jw = random.uniform(score_min - 0.03, min(score_max + 0.03, 1.0))
            ts = random.uniform(score_min - 0.04, min(score_max + 0.02, 1.0))

            status = "reviewed" if tier != "manual_triage" else "pending"
            reviewed_at = now - timedelta(days=random.randint(1, 60)) if status == "reviewed" else None
            matched_at = (reviewed_at or now) - timedelta(hours=random.randint(1, 72))

            match = MatchResult(
                natos_standard_id=std.id,
                cert_link_id=link.id,
                similarity_score=_round(max(0.0, min(1.0, score))),
                levenshtein_score=_round(max(0.0, min(1.0, lev))),
                jaro_winkler_score=_round(max(0.0, min(1.0, jw))),
                token_set_score=_round(max(0.0, min(1.0, ts))),
                confidence_tier=tier,
                status=status,
                matched_at=matched_at,
                reviewed_at=reviewed_at,
            )
            db.add(match)
            matches.append(match)

    db.flush()

    # --- 30 assessments (one per match) ---
    assessments: list[Assessment] = []
    match_pool = list(matches)
    random.shuffle(match_pool)
    match_idx = 0

    for impact, count in ASSESSMENT_IMPACT_DISTRIBUTION:
        for _ in range(count):
            match = match_pool[match_idx]
            match_idx += 1

            action = IMPACT_TO_ACTION[impact]
            decision = "approved" if impact != "safety_critical" else "escalated"
            decided_at = now - timedelta(days=random.randint(1, 45))
            assessor = random.choice(ASSESSORS)

            sig_input = f"{match.id}:{assessor}:{decided_at.isoformat()}".encode()
            signature = hashlib.sha256(sig_input).hexdigest()

            assessment = Assessment(
                match_result_id=match.id,
                assessor_id=assessor,
                impact_classification=impact,
                action_required=action,
                reason_code=f"RC-{impact.upper()}-{random.randint(100, 999)}",
                notes=fake.sentence(nb_words=12),
                decision=decision,
                decided_at=decided_at,
                signature_hash=signature,
            )
            db.add(assessment)
            assessments.append(assessment)

    db.flush()

    # --- 20 notifications (pick first 20 assessments; assign customers via match→link→cert) ---
    from app.models.certificate import Certificate  # local import to avoid cycle

    notifications: list[Notification] = []
    link_by_id = {link.id: link for link in cert_links}
    cert_id_to_customer: dict[UUID, UUID] = {}
    cert_ids = {link.certificate_id for link in cert_links}
    for cert in db.query(Certificate).filter(Certificate.id.in_(cert_ids)).all():
        cert_id_to_customer[cert.id] = cert.customer_id
    customer_lang = {c.id: c.language for c in customers}

    expanded_statuses: list[str] = []
    for status, count in NOTIFICATION_STATUS_MIX:
        expanded_statuses.extend([status] * count)

    for idx in range(20):
        assessment = assessments[idx]
        match = next(m for m in matches if m.id == assessment.match_result_id)
        link = link_by_id[match.cert_link_id]
        customer_id = cert_id_to_customer[link.certificate_id]
        language = customer_lang.get(customer_id, "EN")

        status = expanded_statuses[idx]
        sent_at = now - timedelta(days=random.randint(5, 30))
        delivered_at = sent_at + timedelta(minutes=random.randint(1, 30)) if status in {"delivered", "opened", "clicked", "breached"} else None
        opened_at = (delivered_at + timedelta(hours=random.randint(1, 48))) if status in {"opened", "clicked"} and delivered_at else None
        clicked_at = (opened_at + timedelta(minutes=random.randint(1, 120))) if status == "clicked" and opened_at else None
        sla_deadline = sent_at + timedelta(days=14)

        notification = Notification(
            assessment_id=assessment.id,
            customer_id=customer_id,
            template_language=language,
            subject=f"Certificate action required: {assessment.action_required}",
            body_html=f"<p>{fake.paragraph(nb_sentences=3)}</p>",
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

    # --- 5 sales_escalations (one per breached notification) ---
    escalations: list[SalesEscalation] = []
    for notification in notifications:
        if notification.status != "breached":
            continue
        escalation = SalesEscalation(
            notification_id=notification.id,
            customer_id=notification.customer_id,
            escalation_reason="sla_breach",
            opportunity_value=Decimal(f"{random.randint(5_000, 150_000)}.00"),
            assigned_to=fake.name(),
            status=random.choice(["open", "contacted"]),
            created_at=notification.sla_deadline + timedelta(hours=1),
            resolved_at=None,
        )
        db.add(escalation)
        escalations.append(escalation)

    db.flush()
    return matches, assessments, notifications, escalations
