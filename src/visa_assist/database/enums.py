"""Portable enum values used by the operational schema."""

from enum import StrEnum


class ApplicationStatus(StrEnum):
    SUBMITTED = "submitted"
    BIOMETRICS_SCHEDULED = "biometrics_scheduled"
    BIOMETRICS_COMPLETED = "biometrics_completed"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_DOCUMENTS_REQUESTED = "additional_documents_requested"
    DECISION_RECORDED = "decision_recorded"
    PASSPORT_DISPATCHED = "passport_dispatched"
    CLOSED = "closed"


class ApplicationChannel(StrEnum):
    ONLINE = "online"
    PAPER = "paper"
    ASSISTED = "assisted"


class PriorityService(StrEnum):
    STANDARD = "standard"
    PRIORITY = "priority"
    SUPER_PRIORITY = "super_priority"


class SourceSystem(StrEnum):
    PORTAL = "portal"
    PROCESSING_CENTER = "processing_center"
    BIOMETRICS_PROVIDER = "biometrics_provider"
    COURIER = "courier"


class AppointmentType(StrEnum):
    BIOMETRICS = "biometrics"
    INTERVIEW = "interview"
    DOCUMENT_SUBMISSION = "document_submission"


class AppointmentStatus(StrEnum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    MISSED = "missed"


class CollectionStatus(StrEnum):
    PENDING = "pending"
    COLLECTED = "collected"
    FAILED = "failed"


class ProcessingStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SubmissionStatus(StrEnum):
    NOT_SUBMITTED = "not_submitted"
    REQUESTED = "requested"
    SUBMITTED = "submitted"


class VerificationStatus(StrEnum):
    NOT_REVIEWED = "not_reviewed"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentRequestStatus(StrEnum):
    OPEN = "open"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    CLOSED = "closed"
    OVERDUE = "overdue"


class DecisionType(StrEnum):
    GRANTED = "granted"
    REFUSED = "refused"
    WITHDRAWN = "withdrawn"
    VOID = "void"


class DeliveryStatus(StrEnum):
    AWAITING_RECEIPT = "awaiting_receipt"
    RECEIVED = "received"
    DISPATCHED = "dispatched"
    IN_TRANSIT = "in_transit"
    READY_FOR_COLLECTION = "ready_for_collection"
    DELIVERED = "delivered"
    COLLECTED = "collected"
