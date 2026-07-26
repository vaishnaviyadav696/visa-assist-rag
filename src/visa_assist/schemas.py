"""Pydantic response models for structured operational data."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

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


class OrmResponse(BaseModel):
    """Base response configured to validate SQLAlchemy model instances."""

    model_config = ConfigDict(from_attributes=True)


class ApplicationStatusEventResponse(OrmResponse):
    status_event_id: str
    application_id: str
    status_code: ApplicationStatus
    status_label: str
    status_description: str | None
    event_timestamp: datetime
    source_system: SourceSystem
    location: str | None
    visible_to_applicant: bool


class AppointmentResponse(OrmResponse):
    appointment_id: str
    application_id: str
    appointment_type: AppointmentType
    appointment_date: datetime
    appointment_location: str
    status: AppointmentStatus
    rescheduled_from: str | None
    completed_at: datetime | None


class BiometricEventResponse(OrmResponse):
    biometric_event_id: str
    application_id: str
    appointment_id: str | None
    collection_status: CollectionStatus
    collected_at: datetime | None
    processing_status: ProcessingStatus
    last_updated_at: datetime


class ApplicationDocumentResponse(OrmResponse):
    document_id: str
    application_id: str
    document_type: str
    submission_status: SubmissionStatus
    submitted_at: datetime | None
    verification_status: VerificationStatus
    requested_again: bool
    request_reason: str | None
    last_updated_at: datetime


class AdditionalDocumentRequestResponse(OrmResponse):
    request_id: str
    application_id: str
    document_type: str
    requested_at: datetime
    due_date: datetime | None
    submitted_at: datetime | None
    status: DocumentRequestStatus
    instructions: str | None


class ApplicationDecisionResponse(OrmResponse):
    decision_id: str
    application_id: str
    decision_type: DecisionType
    decision_date: date
    decision_summary: str | None
    refusal_reason_category: str | None
    appeal_available: bool


class PassportTrackingResponse(OrmResponse):
    tracking_id: str
    application_id: str
    passport_received_at: datetime | None
    passport_dispatched_at: datetime | None
    courier_name: str | None
    tracking_number: str | None
    delivery_status: DeliveryStatus
    delivered_at: datetime | None


class VisaApplicationResponse(OrmResponse):
    application_id: str
    user_id: str
    reference_number: str
    destination_country: str
    visa_category: str
    submission_date: date
    current_status: ApplicationStatus
    application_channel: ApplicationChannel
    processing_center: str | None
    priority_service: PriorityService
    expected_decision_date: date | None
    decision_date: date | None
    created_at: datetime
    updated_at: datetime
    status_history: list[ApplicationStatusEventResponse] = Field(default_factory=list)
    appointments: list[AppointmentResponse] = Field(default_factory=list)
    biometric_events: list[BiometricEventResponse] = Field(default_factory=list)
    documents: list[ApplicationDocumentResponse] = Field(default_factory=list)
    document_requests: list[AdditionalDocumentRequestResponse] = Field(
        default_factory=list
    )
    decisions: list[ApplicationDecisionResponse] = Field(default_factory=list)
    passport_tracking: list[PassportTrackingResponse] = Field(default_factory=list)


class UserResponse(OrmResponse):
    user_id: str
    first_name: str
    last_name: str
    email: str
    passport_country: str
    preferred_language: str
    created_at: datetime
    applications: list[VisaApplicationResponse] = Field(default_factory=list)
