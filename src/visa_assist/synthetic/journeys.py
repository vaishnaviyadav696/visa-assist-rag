"""Reviewed templates for coherent synthetic application journeys."""

from dataclasses import dataclass
from enum import StrEnum

from visa_assist.database.enums import ApplicationStatus, SourceSystem


class JourneyKind(StrEnum):
    """Supported synthetic visa journey families."""

    APPROVED = "approved"
    ADDITIONAL_DOCUMENTS = "additional_documents"
    DELAYED = "delayed"
    REFUSED = "refused"
    WITHDRAWN = "withdrawn"
    UNDER_PROCESSING = "under_processing"


@dataclass(frozen=True)
class Milestone:
    """One ordered application status milestone."""

    status: ApplicationStatus
    label: str
    day_offset: int
    source_system: SourceSystem = SourceSystem.PORTAL


@dataclass(frozen=True)
class JourneyTemplate:
    """Ordered status sequence and related-record behavior for a journey."""

    kind: JourneyKind
    milestones: tuple[Milestone, ...]
    decision: bool = False
    tracking: bool = False
    additional_document_request: bool = False

    @property
    def final_status(self) -> ApplicationStatus:
        """Return the final status represented by the journey."""
        return self.milestones[-1].status

    @property
    def duration_days(self) -> int:
        """Return the final milestone offset."""
        return self.milestones[-1].day_offset


JOURNEY_TEMPLATES = {
    JourneyKind.APPROVED: JourneyTemplate(
        kind=JourneyKind.APPROVED,
        decision=True,
        tracking=True,
        milestones=(
            Milestone(ApplicationStatus.SUBMITTED, "Submitted", 0),
            Milestone(ApplicationStatus.APPOINTMENT_BOOKED, "Appointment booked", 5),
            Milestone(
                ApplicationStatus.BIOMETRICS_COMPLETED,
                "Biometrics completed",
                7,
                SourceSystem.BIOMETRICS_PROVIDER,
            ),
            Milestone(
                ApplicationStatus.FORWARDED_FOR_PROCESSING,
                "Forwarded for processing",
                10,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.UNDER_PROCESSING,
                "Under processing",
                12,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.DECISION_MADE,
                "Decision made",
                30,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.PASSPORT_DISPATCHED,
                "Passport dispatched",
                32,
                SourceSystem.COURIER,
            ),
            Milestone(
                ApplicationStatus.DELIVERED,
                "Delivered",
                35,
                SourceSystem.COURIER,
            ),
        ),
    ),
    JourneyKind.ADDITIONAL_DOCUMENTS: JourneyTemplate(
        kind=JourneyKind.ADDITIONAL_DOCUMENTS,
        decision=True,
        additional_document_request=True,
        milestones=(
            Milestone(ApplicationStatus.SUBMITTED, "Submitted", 0),
            Milestone(
                ApplicationStatus.BIOMETRICS_COMPLETED,
                "Biometrics completed",
                7,
                SourceSystem.BIOMETRICS_PROVIDER,
            ),
            Milestone(
                ApplicationStatus.UNDER_PROCESSING,
                "Under processing",
                10,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.ADDITIONAL_DOCUMENTS_REQUESTED,
                "Additional document requested",
                20,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.DOCUMENT_SUBMITTED,
                "Document submitted",
                24,
            ),
            Milestone(
                ApplicationStatus.PROCESSING_RESUMED,
                "Processing resumed",
                25,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.DECISION_MADE,
                "Decision made",
                40,
                SourceSystem.PROCESSING_CENTER,
            ),
        ),
    ),
    JourneyKind.DELAYED: JourneyTemplate(
        kind=JourneyKind.DELAYED,
        decision=True,
        milestones=(
            Milestone(ApplicationStatus.SUBMITTED, "Submitted", 0),
            Milestone(
                ApplicationStatus.BIOMETRICS_COMPLETED,
                "Biometrics completed",
                7,
                SourceSystem.BIOMETRICS_PROVIDER,
            ),
            Milestone(
                ApplicationStatus.UNDER_PROCESSING,
                "Under processing",
                10,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.PROCESSING_DELAY,
                "Processing delay",
                35,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.ESCALATION_RAISED,
                "Escalation raised",
                50,
            ),
            Milestone(
                ApplicationStatus.DECISION_MADE,
                "Decision made",
                70,
                SourceSystem.PROCESSING_CENTER,
            ),
        ),
    ),
    JourneyKind.REFUSED: JourneyTemplate(
        kind=JourneyKind.REFUSED,
        decision=True,
        tracking=True,
        milestones=(
            Milestone(ApplicationStatus.SUBMITTED, "Submitted", 0),
            Milestone(
                ApplicationStatus.BIOMETRICS_COMPLETED,
                "Biometrics completed",
                7,
                SourceSystem.BIOMETRICS_PROVIDER,
            ),
            Milestone(
                ApplicationStatus.UNDER_PROCESSING,
                "Under processing",
                10,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.DECISION_MADE,
                "Decision made",
                30,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.REFUSED,
                "Refused",
                31,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.PASSPORT_RETURNED,
                "Passport returned",
                35,
                SourceSystem.COURIER,
            ),
        ),
    ),
    JourneyKind.WITHDRAWN: JourneyTemplate(
        kind=JourneyKind.WITHDRAWN,
        decision=True,
        milestones=(
            Milestone(ApplicationStatus.SUBMITTED, "Submitted", 0),
            Milestone(
                ApplicationStatus.APPOINTMENT_COMPLETED,
                "Appointment completed",
                5,
                SourceSystem.BIOMETRICS_PROVIDER,
            ),
            Milestone(
                ApplicationStatus.UNDER_PROCESSING,
                "Under processing",
                10,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.WITHDRAWAL_REQUESTED,
                "Withdrawal requested",
                15,
            ),
            Milestone(
                ApplicationStatus.APPLICATION_WITHDRAWN,
                "Application withdrawn",
                16,
                SourceSystem.PROCESSING_CENTER,
            ),
        ),
    ),
    JourneyKind.UNDER_PROCESSING: JourneyTemplate(
        kind=JourneyKind.UNDER_PROCESSING,
        milestones=(
            Milestone(ApplicationStatus.SUBMITTED, "Submitted", 0),
            Milestone(ApplicationStatus.APPOINTMENT_BOOKED, "Appointment booked", 5),
            Milestone(
                ApplicationStatus.BIOMETRICS_COMPLETED,
                "Biometrics completed",
                7,
                SourceSystem.BIOMETRICS_PROVIDER,
            ),
            Milestone(
                ApplicationStatus.FORWARDED_FOR_PROCESSING,
                "Forwarded for processing",
                10,
                SourceSystem.PROCESSING_CENTER,
            ),
            Milestone(
                ApplicationStatus.UNDER_PROCESSING,
                "Under processing",
                12,
                SourceSystem.PROCESSING_CENTER,
            ),
        ),
    ),
}


DEFAULT_JOURNEY_COUNTS = {
    JourneyKind.APPROVED: 45,
    JourneyKind.ADDITIONAL_DOCUMENTS: 30,
    JourneyKind.DELAYED: 25,
    JourneyKind.REFUSED: 20,
    JourneyKind.WITHDRAWN: 10,
    JourneyKind.UNDER_PROCESSING: 20,
}
