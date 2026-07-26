"""Tests for coherent and reproducible synthetic visa journeys."""

from collections import Counter
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from visa_assist.database.base import Base
from visa_assist.database.enums import ApplicationStatus
from visa_assist.database.models import User, VisaApplication
from visa_assist.database.session import (
    create_database_engine,
    create_session_factory,
)
from visa_assist.synthetic.generator import (
    HISTORICAL_EMAIL,
    SyntheticDataExistsError,
    build_synthetic_users,
    generate_synthetic_data,
)
from visa_assist.synthetic.journeys import (
    DEFAULT_JOURNEY_COUNTS,
    JOURNEY_TEMPLATES,
)
from visa_assist.synthetic.validation import (
    SyntheticDataValidationError,
    validate_dataset,
)


def _signature(users: list[User]) -> tuple[tuple[object, ...], ...]:
    """Return a stable projection of generated journeys."""
    return tuple(
        (
            user.user_id,
            user.email,
            tuple(
                (
                    application.application_id,
                    application.reference_number,
                    application.submission_date,
                    tuple(
                        (
                            event.status_event_id,
                            event.status_code,
                            event.event_timestamp,
                        )
                        for event in application.status_history
                    ),
                )
                for application in user.applications
            ),
        )
        for user in users
    )


def test_default_dataset_meets_requested_volumes() -> None:
    """Default generation stays inside every requested volume range."""
    users = build_synthetic_users(seed=42)

    summary = validate_dataset(users, seed=42)

    assert summary.applicants == 100
    assert summary.applications == 150
    assert summary.status_events == 990
    assert summary.documents == 300
    assert summary.appointments == 150
    assert summary.tracking_records == 65
    assert summary.additional_document_requests == 30


def test_generation_is_reproducible_by_seed() -> None:
    """Equal seeds reproduce records while a different seed changes them."""
    first = _signature(build_synthetic_users(seed=42))
    second = _signature(build_synthetic_users(seed=42))
    different = _signature(build_synthetic_users(seed=43))

    assert first == second
    assert first != different


def test_all_journeys_match_reviewed_templates() -> None:
    """Applications use complete templates rather than unrelated random rows."""
    users = build_synthetic_users(seed=42)
    sequences = Counter(
        tuple(event.status_code for event in application.status_history)
        for user in users
        for application in user.applications
    )

    for kind, expected_count in DEFAULT_JOURNEY_COUNTS.items():
        expected_sequence = tuple(
            milestone.status for milestone in JOURNEY_TEMPLATES[kind].milestones
        )
        assert sequences[expected_sequence] == expected_count


def test_historical_applicant_has_required_application_history() -> None:
    """One applicant has approved, refused, and active historical journeys."""
    users = build_synthetic_users(seed=42)
    historical = next(user for user in users if user.email == HISTORICAL_EMAIL)
    by_year = {item.submission_date.year: item for item in historical.applications}

    assert set(by_year) == {2022, 2024, 2026}
    assert by_year[2022].decisions[0].decision_type.value == "granted"
    assert by_year[2024].decisions[0].decision_type.value == "refused"
    assert by_year[2026].current_status is ApplicationStatus.UNDER_PROCESSING
    assert by_year[2026].decision_date is None


def test_statuses_and_related_records_are_chronological() -> None:
    """Journey events and related records follow coherent lifecycle dates."""
    users = build_synthetic_users(seed=42)

    for user in users:
        for application in user.applications:
            event_times = [item.event_timestamp for item in application.status_history]
            assert event_times == sorted(event_times)
            assert (
                application.current_status is application.status_history[-1].status_code
            )
            assert application.submission_date <= application.updated_at.date()
            for appointment in application.appointments:
                assert (
                    appointment.appointment_date.date() >= application.submission_date
                )
                assert appointment.completed_at is not None
                assert appointment.completed_at >= appointment.appointment_date
            for request in application.document_requests:
                assert request.due_date is not None
                assert request.submitted_at is not None
                assert request.requested_at <= request.submitted_at <= request.due_date
            for tracking in application.passport_tracking:
                assert tracking.passport_received_at is not None
                assert tracking.passport_dispatched_at is not None
                assert tracking.delivered_at is not None
                assert (
                    tracking.passport_received_at
                    <= tracking.passport_dispatched_at
                    <= tracking.delivered_at
                )


@pytest.fixture
def database_engine(tmp_path: Path) -> Engine:
    """Create an isolated database for persistence tests."""
    engine = create_database_engine(f"sqlite:///{tmp_path / 'synthetic.db'}")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_persistence_is_transactional_and_requires_replace(
    database_engine: Engine,
) -> None:
    """Persistence is complete and refuses accidental replacement."""
    factory = create_session_factory(database_engine)

    summary = generate_synthetic_data(factory, seed=42)

    assert summary.applications == 150
    with Session(database_engine) as session:
        assert session.scalar(select(func.count()).select_from(User)) == 100
        assert session.scalar(select(func.count()).select_from(VisaApplication)) == 150

    with pytest.raises(SyntheticDataExistsError):
        generate_synthetic_data(factory, seed=43)

    replacement = generate_synthetic_data(factory, seed=43, replace=True)
    assert replacement.seed == 43
    with Session(database_engine) as session:
        first_user = session.scalar(select(User).order_by(User.email))
        assert first_user is not None
        assert first_user.user_id != build_synthetic_users(seed=42)[0].user_id


def test_validation_failure_occurs_before_persistence(
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed pre-commit validation leaves existing rows untouched."""
    factory = create_session_factory(database_engine)
    generate_synthetic_data(factory, seed=42)

    def reject_dataset(users: list[User], *, seed: int):
        del users, seed
        raise SyntheticDataValidationError("forced validation failure")

    monkeypatch.setattr(
        "visa_assist.synthetic.generator.validate_dataset", reject_dataset
    )

    with pytest.raises(SyntheticDataValidationError, match="forced"):
        generate_synthetic_data(factory, seed=43, replace=True)

    with Session(database_engine) as session:
        assert session.scalar(select(func.count()).select_from(User)) == 100


def test_reference_values_are_visibly_synthetic() -> None:
    """Generated identities and references cannot be mistaken for real data."""
    users = build_synthetic_users(seed=42)

    assert all(user.first_name == "Demo" for user in users)
    assert all(user.email.endswith("@example.test") for user in users)
    assert all(
        application.reference_number.startswith("SYNTH-")
        for user in users
        for application in user.applications
    )
    assert date(2022, 1, 1) <= min(
        application.submission_date
        for user in users
        for application in user.applications
    )
