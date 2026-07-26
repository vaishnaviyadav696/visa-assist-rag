"""Build and persist deterministic, coherent synthetic visa journeys."""

import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from visa_assist.database.enums import (
    ApplicationChannel,
    AppointmentStatus,
    AppointmentType,
    CollectionStatus,
    DecisionType,
    DeliveryStatus,
    DocumentRequestStatus,
    PriorityService,
    ProcessingStatus,
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
from visa_assist.database.session import session_scope
from visa_assist.synthetic.journeys import (
    DEFAULT_JOURNEY_COUNTS,
    JOURNEY_TEMPLATES,
    JourneyKind,
    JourneyTemplate,
)
from visa_assist.synthetic.validation import GenerationSummary, validate_dataset

DEFAULT_APPLICANT_COUNT = 100
REFERENCE_DATE = date(2026, 7, 1)
HISTORICAL_EMAIL = "historical.applicant@example.test"
PROCESSING_CENTERS = (
    "Demo Processing Centre North",
    "Demo Processing Centre Central",
    "Demo Processing Centre South",
)
DOCUMENT_TYPES = ("travel_plan", "financial_evidence")


class SyntheticDataExistsError(RuntimeError):
    """Raised when generation would overwrite existing users without consent."""


@dataclass(frozen=True)
class ApplicationSpec:
    """Journey and submission date assigned to one synthetic application."""

    kind: JourneyKind
    submission_date: date


def build_synthetic_users(seed: int = 42) -> list[User]:
    """Build the reviewed 100-applicant dataset without database side effects."""
    rng = random.Random(seed)
    users = [_build_user(seed, index) for index in range(DEFAULT_APPLICANT_COUNT)]

    special_specs = (
        ApplicationSpec(JourneyKind.APPROVED, date(2022, 3, 15)),
        ApplicationSpec(JourneyKind.REFUSED, date(2024, 4, 10)),
        ApplicationSpec(JourneyKind.UNDER_PROCESSING, date(2026, 5, 1)),
    )
    users[0].email = HISTORICAL_EMAIL
    for application_index, spec in enumerate(special_specs):
        users[0].applications.append(
            _build_application(seed, application_index, spec, rng)
        )

    remaining_specs = _remaining_specs(rng)
    application_index = len(special_specs)
    spec_index = 0
    for user_index, user in enumerate(users[1:], start=1):
        application_count = 2 if user_index <= 48 else 1
        for _ in range(application_count):
            spec = remaining_specs[spec_index]
            user.applications.append(
                _build_application(seed, application_index, spec, rng)
            )
            application_index += 1
            spec_index += 1

    validate_dataset(users, seed=seed)
    return users


def generate_synthetic_data(
    factory: sessionmaker[Session],
    *,
    seed: int = 42,
    replace: bool = False,
) -> GenerationSummary:
    """Validate and persist one deterministic dataset transactionally."""
    users = build_synthetic_users(seed)
    summary = validate_dataset(users, seed=seed)

    with session_scope(factory) as session:
        existing = session.scalar(select(func.count()).select_from(User)) or 0
        if existing and not replace:
            raise SyntheticDataExistsError(
                "Synthetic users already exist; pass replace=True to reset them"
            )
        if existing:
            for user in session.scalars(select(User)).all():
                session.delete(user)
            session.flush()
        session.add_all(users)

    return summary


def _build_user(seed: int, index: int) -> User:
    number = index + 1
    return User(
        user_id=_id(seed, "user", number),
        first_name="Demo",
        last_name=f"Applicant {number:03d}",
        email=f"applicant{number:03d}@example.test",
        passport_country="IN",
        preferred_language="en",
        created_at=datetime(2021, 1, 1, 9, 0, tzinfo=UTC) + timedelta(days=index),
    )


def _remaining_specs(rng: random.Random) -> list[ApplicationSpec]:
    remaining_counts = dict(DEFAULT_JOURNEY_COUNTS)
    remaining_counts[JourneyKind.APPROVED] -= 1
    remaining_counts[JourneyKind.REFUSED] -= 1
    remaining_counts[JourneyKind.UNDER_PROCESSING] -= 1

    specs: list[ApplicationSpec] = []
    for kind, count in remaining_counts.items():
        template = JOURNEY_TEMPLATES[kind]
        for _ in range(count):
            if kind is JourneyKind.UNDER_PROCESSING:
                days_before_reference = rng.randint(15, 80)
            else:
                days_before_reference = template.duration_days + rng.randint(30, 900)
            specs.append(
                ApplicationSpec(
                    kind, REFERENCE_DATE - timedelta(days=days_before_reference)
                )
            )
    rng.shuffle(specs)
    return specs


def _build_application(
    seed: int,
    index: int,
    spec: ApplicationSpec,
    rng: random.Random,
) -> VisaApplication:
    template = JOURNEY_TEMPLATES[spec.kind]
    application_number = index + 1
    application_id = _id(seed, "application", application_number)
    decision_date = (
        spec.submission_date + timedelta(days=_decision_offset(template))
        if template.decision
        else None
    )
    final_time = _at_day(spec.submission_date, template.duration_days)
    application = VisaApplication(
        application_id=application_id,
        reference_number=f"SYNTH-{spec.submission_date.year}-{application_number:04d}",
        destination_country="GB",
        visa_category="standard_visitor",
        submission_date=spec.submission_date,
        current_status=template.final_status,
        application_channel=rng.choice(tuple(ApplicationChannel)),
        processing_center=rng.choice(PROCESSING_CENTERS),
        priority_service=rng.choices(tuple(PriorityService), weights=(80, 15, 5), k=1)[
            0
        ],
        expected_decision_date=spec.submission_date
        + timedelta(days=60 if spec.kind is JourneyKind.DELAYED else 30),
        decision_date=decision_date,
        created_at=_at_day(spec.submission_date, 0),
        updated_at=final_time,
    )

    _add_status_history(application, seed, application_number, template)
    appointment = _add_appointment(
        application, seed, application_number, spec.submission_date, spec.kind
    )
    if spec.kind is not JourneyKind.WITHDRAWN:
        _add_biometrics(
            application,
            appointment,
            seed,
            application_number,
            spec.submission_date,
        )
    _add_documents(application, seed, application_number, spec)
    if template.additional_document_request:
        _add_document_request(
            application, seed, application_number, spec.submission_date
        )
    if template.decision:
        _add_decision(application, seed, application_number, spec.kind, decision_date)
    if template.tracking:
        _add_tracking(application, seed, application_number, spec)
    return application


def _add_status_history(
    application: VisaApplication,
    seed: int,
    application_number: int,
    template: JourneyTemplate,
) -> None:
    for event_index, milestone in enumerate(template.milestones, start=1):
        application.status_history.append(
            ApplicationStatusEvent(
                status_event_id=_id(seed, f"status-{application_number}", event_index),
                status_code=milestone.status,
                status_label=milestone.label,
                status_description=(
                    f"Synthetic {milestone.label.lower()} event for demonstration."
                ),
                event_timestamp=_at_day(
                    application.submission_date, milestone.day_offset
                ),
                source_system=milestone.source_system,
                location=(
                    application.processing_center
                    if milestone.source_system.value != "portal"
                    else None
                ),
                visible_to_applicant=True,
            )
        )


def _add_appointment(
    application: VisaApplication,
    seed: int,
    application_number: int,
    submission_date: date,
    kind: JourneyKind,
) -> Appointment:
    appointment_time = _at_day(submission_date, 5)
    completed_offset = 5 if kind is JourneyKind.WITHDRAWN else 7
    appointment = Appointment(
        appointment_id=_id(seed, "appointment", application_number),
        appointment_type=AppointmentType.BIOMETRICS,
        appointment_date=appointment_time,
        appointment_location="Demo Visa Application Centre",
        status=AppointmentStatus.COMPLETED,
        completed_at=_at_day(submission_date, completed_offset) + timedelta(hours=1),
    )
    application.appointments.append(appointment)
    return appointment


def _add_biometrics(
    application: VisaApplication,
    appointment: Appointment,
    seed: int,
    application_number: int,
    submission_date: date,
) -> None:
    collected_at = _at_day(submission_date, 7) + timedelta(hours=1)
    application.biometric_events.append(
        BiometricEvent(
            biometric_event_id=_id(seed, "biometric", application_number),
            appointment=appointment,
            collection_status=CollectionStatus.COLLECTED,
            collected_at=collected_at,
            processing_status=ProcessingStatus.COMPLETED,
            last_updated_at=collected_at + timedelta(hours=4),
        )
    )


def _add_documents(
    application: VisaApplication,
    seed: int,
    application_number: int,
    spec: ApplicationSpec,
) -> None:
    for document_index, document_type in enumerate(DOCUMENT_TYPES, start=1):
        application.documents.append(
            ApplicationDocument(
                document_id=_id(seed, f"document-{application_number}", document_index),
                document_type=document_type,
                submission_status=SubmissionStatus.SUBMITTED,
                submitted_at=_at_day(spec.submission_date, 0),
                verification_status=VerificationStatus.VERIFIED,
                requested_again=(
                    spec.kind is JourneyKind.ADDITIONAL_DOCUMENTS
                    and document_type == "travel_plan"
                ),
                request_reason=(
                    "Updated synthetic travel plan requested."
                    if spec.kind is JourneyKind.ADDITIONAL_DOCUMENTS
                    and document_type == "travel_plan"
                    else None
                ),
                last_updated_at=_at_day(
                    spec.submission_date,
                    24 if spec.kind is JourneyKind.ADDITIONAL_DOCUMENTS else 1,
                ),
            )
        )


def _add_document_request(
    application: VisaApplication,
    seed: int,
    application_number: int,
    submission_date: date,
) -> None:
    requested_at = _at_day(submission_date, 20)
    application.document_requests.append(
        AdditionalDocumentRequest(
            request_id=_id(seed, "request", application_number),
            document_type="travel_plan",
            requested_at=requested_at,
            due_date=requested_at + timedelta(days=10),
            submitted_at=_at_day(submission_date, 24),
            status=DocumentRequestStatus.CLOSED,
            instructions="Submit an updated synthetic travel plan.",
        )
    )


def _add_decision(
    application: VisaApplication,
    seed: int,
    application_number: int,
    kind: JourneyKind,
    decision_date: date | None,
) -> None:
    if decision_date is None:
        raise ValueError("Decision journey is missing a decision date")
    if kind is JourneyKind.REFUSED:
        decision_type = DecisionType.REFUSED
        refusal_category = "synthetic_eligibility_assessment"
        appeal_available = True
    elif kind is JourneyKind.WITHDRAWN:
        decision_type = DecisionType.WITHDRAWN
        refusal_category = None
        appeal_available = False
    else:
        decision_type = DecisionType.GRANTED
        refusal_category = None
        appeal_available = False

    application.decisions.append(
        ApplicationDecision(
            decision_id=_id(seed, "decision", application_number),
            decision_type=decision_type,
            decision_date=decision_date,
            decision_summary=f"Synthetic {decision_type.value} decision.",
            refusal_reason_category=refusal_category,
            appeal_available=appeal_available,
        )
    )


def _add_tracking(
    application: VisaApplication,
    seed: int,
    application_number: int,
    spec: ApplicationSpec,
) -> None:
    decision_offset = _decision_offset(JOURNEY_TEMPLATES[spec.kind])
    received_at = _at_day(spec.submission_date, decision_offset)
    dispatched_at = received_at + timedelta(days=2)
    delivered_at = _at_day(
        spec.submission_date, JOURNEY_TEMPLATES[spec.kind].duration_days
    )
    application.passport_tracking.append(
        PassportTracking(
            tracking_id=_id(seed, "tracking", application_number),
            passport_received_at=received_at,
            passport_dispatched_at=dispatched_at,
            courier_name="Demo Courier",
            tracking_number=f"SYNTH-TRACK-{application_number:05d}",
            delivery_status=DeliveryStatus.DELIVERED,
            delivered_at=delivered_at,
        )
    )


def _decision_offset(template: JourneyTemplate) -> int:
    for milestone in reversed(template.milestones):
        if milestone.status.value in {
            "decision_made",
            "application_withdrawn",
        }:
            return milestone.day_offset
    raise ValueError(f"Journey {template.kind.value} has no decision milestone")


def _at_day(submission_date: date, day_offset: int) -> datetime:
    return datetime.combine(
        submission_date + timedelta(days=day_offset),
        time(hour=9),
        tzinfo=UTC,
    )


def _id(seed: int, entity: str, number: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"visa-assist:{seed}:{entity}:{number}"))
