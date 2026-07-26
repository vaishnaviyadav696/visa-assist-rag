"""SQLAlchemy models for synthetic visa-application operations."""

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from visa_assist.database.base import Base, new_id, utc_now
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


def enum_type(enum_class: type[StrEnum], name: str) -> Enum:
    """Create a string-backed enum portable across SQLite and PostgreSQL."""
    return Enum(
        enum_class,
        name=name,
        native_enum=False,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
    )


class User(Base):
    """Synthetic portal user and root ownership record."""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    passport_country: Mapped[str] = mapped_column(String(2))
    preferred_language: Mapped[str] = mapped_column(String(16), default="en")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    applications: Mapped[list["VisaApplication"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class VisaApplication(Base):
    """Current or historical synthetic visa application."""

    __tablename__ = "visa_applications"
    __table_args__ = (
        CheckConstraint(
            "expected_decision_date IS NULL OR "
            "expected_decision_date >= submission_date",
            name="expected_decision_after_submission",
        ),
        CheckConstraint(
            "decision_date IS NULL OR decision_date >= submission_date",
            name="decision_after_submission",
        ),
        Index("ix_visa_applications_user_status", "user_id", "current_status"),
    )

    application_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_id
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True
    )
    reference_number: Mapped[str] = mapped_column(String(64), unique=True)
    destination_country: Mapped[str] = mapped_column(String(2))
    visa_category: Mapped[str] = mapped_column(String(100))
    submission_date: Mapped[date] = mapped_column(Date)
    current_status: Mapped[ApplicationStatus] = mapped_column(
        enum_type(ApplicationStatus, "application_status")
    )
    application_channel: Mapped[ApplicationChannel] = mapped_column(
        enum_type(ApplicationChannel, "application_channel")
    )
    processing_center: Mapped[str | None] = mapped_column(String(200))
    priority_service: Mapped[PriorityService] = mapped_column(
        enum_type(PriorityService, "priority_service"),
        default=PriorityService.STANDARD,
    )
    expected_decision_date: Mapped[date | None] = mapped_column(Date)
    decision_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    user: Mapped[User] = relationship(back_populates="applications")
    status_history: Mapped[list["ApplicationStatusEvent"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationStatusEvent.event_timestamp",
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    biometric_events: Mapped[list["BiometricEvent"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    documents: Mapped[list["ApplicationDocument"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    document_requests: Mapped[list["AdditionalDocumentRequest"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    decisions: Mapped[list["ApplicationDecision"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    passport_tracking: Mapped[list["PassportTracking"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )


class ApplicationStatusEvent(Base):
    """Applicant-visible or internal application status event."""

    __tablename__ = "application_status_history"
    __table_args__ = (
        Index(
            "ix_application_status_history_application_time",
            "application_id",
            "event_timestamp",
        ),
    )

    status_event_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_id
    )
    application_id: Mapped[str] = mapped_column(
        ForeignKey("visa_applications.application_id", ondelete="CASCADE")
    )
    status_code: Mapped[ApplicationStatus] = mapped_column(
        enum_type(ApplicationStatus, "status_event_code")
    )
    status_label: Mapped[str] = mapped_column(String(150))
    status_description: Mapped[str | None] = mapped_column(Text)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_system: Mapped[SourceSystem] = mapped_column(
        enum_type(SourceSystem, "source_system")
    )
    location: Mapped[str | None] = mapped_column(String(200))
    visible_to_applicant: Mapped[bool] = mapped_column(Boolean, default=True)

    application: Mapped[VisaApplication] = relationship(
        back_populates="status_history"
    )


class Appointment(Base):
    """Appointment associated with an application."""

    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= appointment_date",
            name="completion_after_appointment",
        ),
    )

    appointment_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_id
    )
    application_id: Mapped[str] = mapped_column(
        ForeignKey("visa_applications.application_id", ondelete="CASCADE"),
        index=True,
    )
    appointment_type: Mapped[AppointmentType] = mapped_column(
        enum_type(AppointmentType, "appointment_type")
    )
    appointment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    appointment_location: Mapped[str] = mapped_column(String(200))
    status: Mapped[AppointmentStatus] = mapped_column(
        enum_type(AppointmentStatus, "appointment_status")
    )
    rescheduled_from: Mapped[str | None] = mapped_column(
        ForeignKey("appointments.appointment_id", ondelete="SET NULL")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    application: Mapped[VisaApplication] = relationship(back_populates="appointments")
    previous_appointment: Mapped["Appointment | None"] = relationship(
        remote_side="Appointment.appointment_id", foreign_keys=[rescheduled_from]
    )
    biometric_events: Mapped[list["BiometricEvent"]] = relationship(
        back_populates="appointment"
    )


class BiometricEvent(Base):
    """Biometric collection and processing state."""

    __tablename__ = "biometric_events"

    biometric_event_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_id
    )
    application_id: Mapped[str] = mapped_column(
        ForeignKey("visa_applications.application_id", ondelete="CASCADE"),
        index=True,
    )
    appointment_id: Mapped[str | None] = mapped_column(
        ForeignKey("appointments.appointment_id", ondelete="SET NULL")
    )
    collection_status: Mapped[CollectionStatus] = mapped_column(
        enum_type(CollectionStatus, "collection_status")
    )
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        enum_type(ProcessingStatus, "processing_status")
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    application: Mapped[VisaApplication] = relationship(
        back_populates="biometric_events"
    )
    appointment: Mapped[Appointment | None] = relationship(
        back_populates="biometric_events"
    )


class ApplicationDocument(Base):
    """Safe metadata for a synthetic application document."""

    __tablename__ = "application_documents"

    document_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_id
    )
    application_id: Mapped[str] = mapped_column(
        ForeignKey("visa_applications.application_id", ondelete="CASCADE"),
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(100))
    submission_status: Mapped[SubmissionStatus] = mapped_column(
        enum_type(SubmissionStatus, "document_submission_status")
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_status: Mapped[VerificationStatus] = mapped_column(
        enum_type(VerificationStatus, "verification_status")
    )
    requested_again: Mapped[bool] = mapped_column(Boolean, default=False)
    request_reason: Mapped[str | None] = mapped_column(Text)
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    application: Mapped[VisaApplication] = relationship(back_populates="documents")


class AdditionalDocumentRequest(Base):
    """Request for additional application evidence."""

    __tablename__ = "additional_document_requests"
    __table_args__ = (
        CheckConstraint(
            "due_date IS NULL OR due_date >= requested_at",
            name="due_after_request",
        ),
        CheckConstraint(
            "submitted_at IS NULL OR submitted_at >= requested_at",
            name="submission_after_request",
        ),
    )

    request_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_id
    )
    application_id: Mapped[str] = mapped_column(
        ForeignKey("visa_applications.application_id", ondelete="CASCADE"),
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(100))
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[DocumentRequestStatus] = mapped_column(
        enum_type(DocumentRequestStatus, "document_request_status")
    )
    instructions: Mapped[str | None] = mapped_column(Text)

    application: Mapped[VisaApplication] = relationship(
        back_populates="document_requests"
    )


class ApplicationDecision(Base):
    """Decision recorded for a synthetic application."""

    __tablename__ = "application_decisions"
    __table_args__ = (
        CheckConstraint(
            "(decision_type = 'refused' AND refusal_reason_category IS NOT NULL) "
            "OR decision_type != 'refused'",
            name="refusal_has_reason_category",
        ),
    )

    decision_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_id
    )
    application_id: Mapped[str] = mapped_column(
        ForeignKey("visa_applications.application_id", ondelete="CASCADE"),
        index=True,
    )
    decision_type: Mapped[DecisionType] = mapped_column(
        enum_type(DecisionType, "decision_type")
    )
    decision_date: Mapped[date] = mapped_column(Date)
    decision_summary: Mapped[str | None] = mapped_column(Text)
    refusal_reason_category: Mapped[str | None] = mapped_column(String(100))
    appeal_available: Mapped[bool] = mapped_column(Boolean, default=False)

    application: Mapped[VisaApplication] = relationship(back_populates="decisions")


class PassportTracking(Base):
    """Synthetic passport return and courier tracking metadata."""

    __tablename__ = "passport_tracking"
    __table_args__ = (
        CheckConstraint(
            "passport_dispatched_at IS NULL OR passport_received_at IS NULL OR "
            "passport_dispatched_at >= passport_received_at",
            name="dispatch_after_receipt",
        ),
        CheckConstraint(
            "delivered_at IS NULL OR passport_dispatched_at IS NULL OR "
            "delivered_at >= passport_dispatched_at",
            name="delivery_after_dispatch",
        ),
    )

    tracking_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_id
    )
    application_id: Mapped[str] = mapped_column(
        ForeignKey("visa_applications.application_id", ondelete="CASCADE"),
        index=True,
    )
    passport_received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    passport_dispatched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    courier_name: Mapped[str | None] = mapped_column(String(150))
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    delivery_status: Mapped[DeliveryStatus] = mapped_column(
        enum_type(DeliveryStatus, "delivery_status")
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    application: Mapped[VisaApplication] = relationship(
        back_populates="passport_tracking"
    )
