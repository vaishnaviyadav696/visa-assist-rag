"""Validation for generated synthetic visa journeys."""

from dataclasses import dataclass

from visa_assist.database.models import User, VisaApplication
from visa_assist.synthetic.journeys import JOURNEY_TEMPLATES, JourneyKind


class SyntheticDataValidationError(ValueError):
    """Raised when a generated dataset violates its design contract."""


@dataclass(frozen=True)
class GenerationSummary:
    """Validated record counts for one synthetic dataset."""

    seed: int
    applicants: int
    applications: int
    status_events: int
    documents: int
    appointments: int
    tracking_records: int
    additional_document_requests: int


def validate_dataset(users: list[User], *, seed: int) -> GenerationSummary:
    """Validate volume, chronology, identity, and journey consistency."""
    applications = [application for user in users for application in user.applications]

    if len(users) != 100:
        raise SyntheticDataValidationError("Dataset must contain 100 applicants")
    if not 150 <= len(applications) <= 250:
        raise SyntheticDataValidationError("Application count is outside 150-250")

    _validate_synthetic_users(users)
    _validate_unique_ids(users, applications)
    journey_kinds = _validate_applications(applications)
    _validate_historical_applicant(users)

    missing_journeys = set(JourneyKind) - journey_kinds
    if missing_journeys:
        names = ", ".join(sorted(kind.value for kind in missing_journeys))
        raise SyntheticDataValidationError(f"Missing journey families: {names}")

    summary = GenerationSummary(
        seed=seed,
        applicants=len(users),
        applications=len(applications),
        status_events=sum(len(item.status_history) for item in applications),
        documents=sum(len(item.documents) for item in applications),
        appointments=sum(len(item.appointments) for item in applications),
        tracking_records=sum(len(item.passport_tracking) for item in applications),
        additional_document_requests=sum(
            len(item.document_requests) for item in applications
        ),
    )
    _validate_volume(summary)
    return summary


def _validate_synthetic_users(users: list[User]) -> None:
    for user in users:
        if user.first_name != "Demo" or not user.last_name.startswith("Applicant "):
            raise SyntheticDataValidationError(
                "Applicant names must be visibly synthetic"
            )
        if not user.email.endswith("@example.test"):
            raise SyntheticDataValidationError("Applicant emails must use example.test")


def _validate_unique_ids(
    users: list[User], applications: list[VisaApplication]
) -> None:
    identifiers = [user.user_id for user in users]
    identifiers.extend(application.application_id for application in applications)
    for application in applications:
        identifiers.extend(item.status_event_id for item in application.status_history)
        identifiers.extend(item.appointment_id for item in application.appointments)
        identifiers.extend(
            item.biometric_event_id for item in application.biometric_events
        )
        identifiers.extend(item.document_id for item in application.documents)
        identifiers.extend(item.request_id for item in application.document_requests)
        identifiers.extend(item.decision_id for item in application.decisions)
        identifiers.extend(item.tracking_id for item in application.passport_tracking)

    if len(identifiers) != len(set(identifiers)):
        raise SyntheticDataValidationError(
            "Synthetic record identifiers must be unique"
        )


def _validate_applications(applications: list[VisaApplication]) -> set[JourneyKind]:
    matched_kinds: set[JourneyKind] = set()
    template_sequences = {
        tuple(milestone.status for milestone in template.milestones): kind
        for kind, template in JOURNEY_TEMPLATES.items()
    }

    for application in applications:
        events = application.status_history
        timestamps = [event.event_timestamp for event in events]
        if timestamps != sorted(timestamps):
            raise SyntheticDataValidationError("Status events must be chronological")
        if not events or application.current_status != events[-1].status_code:
            raise SyntheticDataValidationError(
                "Application current status must match its final event"
            )
        sequence = tuple(event.status_code for event in events)
        kind = template_sequences.get(sequence)
        if kind is None:
            raise SyntheticDataValidationError("Application has an unknown journey")
        matched_kinds.add(kind)

        if len(application.documents) != 2:
            raise SyntheticDataValidationError(
                "Every application must have two safe document records"
            )
        if len(application.appointments) != 1:
            raise SyntheticDataValidationError(
                "Every application must have one appointment"
            )
        if kind is JourneyKind.ADDITIONAL_DOCUMENTS:
            if len(application.document_requests) != 1:
                raise SyntheticDataValidationError(
                    "Additional-document journeys require one request"
                )
        elif application.document_requests:
            raise SyntheticDataValidationError("Unexpected additional-document request")

        template = JOURNEY_TEMPLATES[kind]
        if template.decision != bool(application.decisions):
            raise SyntheticDataValidationError("Decision record does not match journey")
        if template.tracking != bool(application.passport_tracking):
            raise SyntheticDataValidationError("Tracking record does not match journey")

    return matched_kinds


def _validate_historical_applicant(users: list[User]) -> None:
    historical = next(
        (user for user in users if user.email == "historical.applicant@example.test"),
        None,
    )
    if historical is None:
        raise SyntheticDataValidationError("Historical applicant is missing")

    by_year = {item.submission_date.year: item for item in historical.applications}
    expected_years = {2022, 2024, 2026}
    if set(by_year) != expected_years:
        raise SyntheticDataValidationError(
            "Historical applicant must have 2022, 2024, and 2026 applications"
        )

    sequences = {
        year: tuple(event.status_code for event in application.status_history)
        for year, application in by_year.items()
    }
    approved = tuple(
        item.status for item in JOURNEY_TEMPLATES[JourneyKind.APPROVED].milestones
    )
    refused = tuple(
        item.status for item in JOURNEY_TEMPLATES[JourneyKind.REFUSED].milestones
    )
    processing = tuple(
        item.status
        for item in JOURNEY_TEMPLATES[JourneyKind.UNDER_PROCESSING].milestones
    )
    if sequences != {2022: approved, 2024: refused, 2026: processing}:
        raise SyntheticDataValidationError("Historical applicant journeys are invalid")


def _validate_volume(summary: GenerationSummary) -> None:
    ranges = {
        "status_events": (500, 1_000),
        "documents": (200, 400),
        "appointments": (100, 200),
        "tracking_records": (50, 100),
        "additional_document_requests": (20, 50),
    }
    for name, (minimum, maximum) in ranges.items():
        value = getattr(summary, name)
        if not minimum <= value <= maximum:
            raise SyntheticDataValidationError(
                f"{name} count {value} is outside {minimum}-{maximum}"
            )
