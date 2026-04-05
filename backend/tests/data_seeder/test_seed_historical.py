import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.match_result import MatchResult
from app.models.notification import Notification
from data_seeder.seed_certificates import seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_historical import seed_historical
from data_seeder.seed_standards import seed_standards


def _bootstrap(db_session: Session):
    random.seed(42)
    Faker.seed(42)
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    _, links = seed_certificates_and_links(db_session, customers, standards)
    return standards, links, customers


def test_seed_historical_creates_30_matches(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    assert len(matches) == 30
    assert db_session.query(MatchResult).count() == 30


def test_match_confidence_tier_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(m.confidence_tier for m in matches)
    assert counts["auto_match"] == 10
    assert counts["expert_review"] == 15
    assert counts["manual_triage"] == 5


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


def test_seed_historical_creates_30_assessments(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    assert len(assessments) == 30
    assert db_session.query(Assessment).count() == 30


def test_assessment_impact_classification_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(a.impact_classification for a in assessments)
    assert counts["no_change"] == 10
    assert counts["minor_technical"] == 10
    assert counts["major_technical"] == 5
    assert counts["safety_critical"] == 5


def test_seed_historical_creates_20_notifications(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, _ = seed_historical(db_session, standards, links, customers)
    assert len(notifications) == 20
    assert db_session.query(Notification).count() == 20


def test_seed_historical_creates_5_escalations_for_breached(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, escalations = seed_historical(db_session, standards, links, customers)
    assert len(escalations) == 5
    breached_ids = {n.id for n in notifications if n.status == "breached"}
    assert {e.notification_id for e in escalations} == breached_ids


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
