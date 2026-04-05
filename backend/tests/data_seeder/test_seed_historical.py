from collections import Counter

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.match_result import MatchResult
from app.models.notification import Notification
from data_seeder.seed_certificates import seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_historical import seed_historical
from data_seeder.seed_standards import seed_standards


def _bootstrap(db_session: Session):
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    _, links = seed_certificates_and_links(db_session, customers, standards)
    return standards, links, customers


def test_seed_historical_creates_10_matches(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    assert len(matches) == 10
    assert db_session.query(MatchResult).count() == 10


def test_match_confidence_tier_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(m.confidence_tier for m in matches)
    assert counts["auto_match"] == 5
    assert counts["expert_review"] == 3
    assert counts["manual_triage"] == 2


def test_match_similarity_scores_match_tier_bands(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    for m in matches:
        score = float(m.similarity_score)
        if m.confidence_tier == "auto_match":
            assert score > 0.95
        elif m.confidence_tier == "expert_review":
            assert 0.70 <= score <= 0.95
        elif m.confidence_tier == "manual_triage":
            assert score < 0.70


def test_seed_historical_creates_10_assessments(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    assert len(assessments) == 10
    assert db_session.query(Assessment).count() == 10


def test_assessment_impact_classification_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(a.impact_classification for a in assessments)
    # no_change: assessments 0,1,2,9 → 4 (but 9 has no_change too)
    # Let's assert exact curated values:
    assert counts["no_change"] == 4          # match 0,1,2,9
    assert counts["administrative"] == 2     # match 3,4
    assert counts["minor_technical"] == 2    # match 5,6
    assert counts["major_technical"] == 1    # match 7
    assert counts["safety_critical"] == 1    # match 8


def test_assessment_decision_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(a.decision for a in assessments)
    assert counts["approved"] == 7
    assert counts["escalated"] == 1   # major_technical IEC 60601-1
    assert counts["rejected"] == 2    # safety_critical + manual_triage no_change


def test_seed_historical_creates_8_notifications(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, _ = seed_historical(db_session, standards, links, customers)
    assert len(notifications) == 8
    assert db_session.query(Notification).count() == 8


def test_seed_historical_breached_notification_count(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, _ = seed_historical(db_session, standards, links, customers)
    breached = [n for n in notifications if n.status == "breached"]
    assert len(breached) == 2


def test_seed_historical_creates_3_escalations(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, escalations = seed_historical(db_session, standards, links, customers)
    assert len(escalations) == 3


def test_historical_seeder_referential_integrity(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, assessments, notifications, escalations = seed_historical(
        db_session, standards, links, customers
    )
    match_ids = {m.id for m in matches}
    for a in assessments:
        assert a.match_result_id in match_ids

    assessment_ids = {a.id for a in assessments}
    for n in notifications:
        assert n.assessment_id in assessment_ids

    notification_ids = {n.id for n in notifications}
    for e in escalations:
        assert e.notification_id in notification_ids


def test_notifications_have_tuv_branded_subject(db_session: Session) -> None:
    """Notification subjects must start with 'TÜV Rheinland'."""
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, _ = seed_historical(db_session, standards, links, customers)
    for n in notifications:
        assert n.subject.startswith("TÜV Rheinland"), f"Bad subject: {n.subject!r}"
