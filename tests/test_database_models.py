"""Unit tests for structured operational database models."""

from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import Engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from visa_assist.database.base import Base
from visa_assist.database.enums import (
    ApplicationChannel,
    ApplicationStatus,
    AppointmentStatus,
    AppointmentType,
    CollectionStatus,
    DecisionType,
    DeliveryStatus,
    DocumentRequestStatus,
    PriorityService,
    ProcessingStatus,
    SourceSystem,
    SubmissionStatus,
    VerificationStatus,
)
from visa_assist.database.models import (
    AdditionalDocumentRequest,
    ApplicationDecision,
    ApplicationDocument,
    ApplicationStatusEvent,
    Appointment,
    BiometricEvent,
    PassportTracking,
    User,
    VisaApplication,
)
from visa_assist.database.session import (
    create_database_engine,
    create_session_factory,
    session_scope,
)
from visa_assist.schemas import UserResponse


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    """Create an isolated SQLite database for each test."""
    database = create_database_engine(f"sqlite:///{tmp_path / 'models.db'}")
    Base.metadata.create_all(database)
    yield database
    database.dispose()


def test_metadata_creates_all_operational_tables(engine: Engine) -> None:
    """Declarative metadata creates the complete initial table set."""
    assert set(inspect(engine).get_table_names()) == {
        "additional_document_requests",
        "application_decisions",
        "application_documents",
        "application_status_history",
        "appointments",
        "biometric_events",
        "passport_tracking",
        "users",
        "visa_applications",
    }


def test_models_persist_relationships_and_build_response(engine: Engine) -> None:
    """All model types persist through their application relationships."""
    now = datetime(2026, 7, 26, 10, 0, tzinfo=UTC)
    user = User(
        first_name="Demo",
        last_name="Applicant",
        email="demo.applicant@example.test",
        passport_country="IN",
        preferred_language="en",
    )
    application = VisaApplication(
        reference_number="SYNTH-APP-001",
        destination_country="GB",
        visa_category="standard_visitor",
        submission_date=date(2026, 7, 1),
        current_status=ApplicationStatus.ADDITIONAL_DOCUMENTS_REQUESTED,
        application_channel=ApplicationChannel.ONLINE,
        processing_center="Demo Processing Centre",
        priority_service=PriorityService.STANDARD,
        expected_decision_date=date(2026, 8, 1),
    )
    appointment = Appointment(
        appointment_type=AppointmentType.BIOMETRICS,
        appointment_date=now,
        appointment_location="Demo Visa Centre",
        status=AppointmentStatus.COMPLETED,
        completed_at=now + timedelta(minutes=30),
    )
    application.status_history.append(
        ApplicationStatusEvent(
            status_code=ApplicationStatus.SUBMITTED,
            status_label="Submitted",
            status_description="Synthetic submission recorded.",
            event_timestamp=now - timedelta(days=25),
            source_system=SourceSystem.PORTAL,
            location=None,
            visible_to_applicant=True,
        )
    )
    application.appointments.append(appointment)
    application.biometric_events.append(
        BiometricEvent(
            appointment=appointment,
            collection_status=CollectionStatus.COLLECTED,
            collected_at=now + timedelta(minutes=20),
            processing_status=ProcessingStatus.COMPLETED,
        )
    )
    application.documents.append(
        ApplicationDocument(
            document_type="financial_evidence",
            submission_status=SubmissionStatus.SUBMITTED,
            submitted_at=now,
            verification_status=VerificationStatus.PENDING,
            requested_again=False,
        )
    )
    application.document_requests.append(
        AdditionalDocumentRequest(
            document_type="travel_plan",
            requested_at=now,
            due_date=now + timedelta(days=7),
            status=DocumentRequestStatus.OPEN,
            instructions="Upload a synthetic fixture only.",
        )
    )
    application.decisions.append(
        ApplicationDecision(
            decision_type=DecisionType.GRANTED,
            decision_date=date(2026, 7, 26),
            decision_summary="Synthetic decision record.",
            appeal_available=False,
        )
    )
    application.passport_tracking.append(
        PassportTracking(
            passport_received_at=now,
            passport_dispatched_at=now + timedelta(hours=2),
            courier_name="Demo Courier",
            tracking_number="SYNTH-TRACK-001",
            delivery_status=DeliveryStatus.DISPATCHED,
        )
    )
    user.applications.append(application)

    factory = create_session_factory(engine)
    with session_scope(factory) as session:
        session.add(user)

    with Session(engine) as session:
        stored_user = session.scalar(select(User).where(User.email == user.email))
        assert stored_user is not None
        assert len(stored_user.applications) == 1
        stored_application = stored_user.applications[0]
        assert len(stored_application.status_history) == 1
        assert len(stored_application.appointments) == 1
        assert len(stored_application.biometric_events) == 1
        assert len(stored_application.documents) == 1
        assert len(stored_application.document_requests) == 1
        assert len(stored_application.decisions) == 1
        assert len(stored_application.passport_tracking) == 1

        response = UserResponse.model_validate(stored_user)
        assert response.user_id == stored_user.user_id
        assert response.applications[0].reference_number == "SYNTH-APP-001"
        assert response.applications[0].status_history[0].status_label == "Submitted"


def test_unique_email_constraint(engine: Engine) -> None:
    """Duplicate synthetic user emails are rejected."""
    factory = create_session_factory(engine)
    with pytest.raises(IntegrityError), session_scope(factory) as session:
        session.add_all(
            [
                User(
                    first_name="Demo",
                    last_name="One",
                    email="duplicate@example.test",
                    passport_country="IN",
                ),
                User(
                    first_name="Demo",
                    last_name="Two",
                    email="duplicate@example.test",
                    passport_country="IN",
                ),
            ]
        )


def test_application_date_constraint(engine: Engine) -> None:
    """An expected decision cannot precede application submission."""
    factory = create_session_factory(engine)
    user = User(
        first_name="Demo",
        last_name="Dates",
        email="dates@example.test",
        passport_country="IN",
    )
    user.applications.append(
        VisaApplication(
            reference_number="SYNTH-DATES-001",
            destination_country="GB",
            visa_category="standard_visitor",
            submission_date=date(2026, 7, 10),
            current_status=ApplicationStatus.SUBMITTED,
            application_channel=ApplicationChannel.ONLINE,
            priority_service=PriorityService.STANDARD,
            expected_decision_date=date(2026, 7, 1),
        )
    )

    with pytest.raises(IntegrityError), session_scope(factory) as session:
        session.add(user)
