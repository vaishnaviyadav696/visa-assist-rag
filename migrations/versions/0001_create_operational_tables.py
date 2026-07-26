"""Create the structured operational tables.

Revision ID: 0001
Revises: None
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


application_status = sa.Enum(
    "submitted",
    "biometrics_scheduled",
    "biometrics_completed",
    "under_review",
    "additional_documents_requested",
    "decision_recorded",
    "passport_dispatched",
    "closed",
    name="application_status",
    native_enum=False,
)
application_channel = sa.Enum(
    "online", "paper", "assisted", name="application_channel", native_enum=False
)
priority_service = sa.Enum(
    "standard", "priority", "super_priority", name="priority_service", native_enum=False
)


def upgrade() -> None:
    """Create operational tables, constraints, and indexes."""
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(36), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("passport_country", sa.String(2), nullable=False),
        sa.Column("preferred_language", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "visa_applications",
        sa.Column("application_id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("reference_number", sa.String(64), nullable=False),
        sa.Column("destination_country", sa.String(2), nullable=False),
        sa.Column("visa_category", sa.String(100), nullable=False),
        sa.Column("submission_date", sa.Date(), nullable=False),
        sa.Column("current_status", application_status, nullable=False),
        sa.Column("application_channel", application_channel, nullable=False),
        sa.Column("processing_center", sa.String(200)),
        sa.Column("priority_service", priority_service, nullable=False),
        sa.Column("expected_decision_date", sa.Date()),
        sa.Column("decision_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "expected_decision_date IS NULL OR "
            "expected_decision_date >= submission_date",
            name="ck_visa_applications_expected_decision_after_submission",
        ),
        sa.CheckConstraint(
            "decision_date IS NULL OR decision_date >= submission_date",
            name="ck_visa_applications_decision_after_submission",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], ondelete="CASCADE",
            name="fk_visa_applications_user_id_users",
        ),
        sa.UniqueConstraint(
            "reference_number", name="uq_visa_applications_reference_number"
        ),
    )
    op.create_index("ix_visa_applications_user_id", "visa_applications", ["user_id"])
    op.create_index(
        "ix_visa_applications_user_status",
        "visa_applications",
        ["user_id", "current_status"],
    )

    op.create_table(
        "application_status_history",
        sa.Column("status_event_id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), nullable=False),
        sa.Column(
            "status_code",
            sa.Enum(
                "submitted", "biometrics_scheduled", "biometrics_completed",
                "under_review", "additional_documents_requested",
                "decision_recorded", "passport_dispatched", "closed",
                name="status_event_code", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("status_label", sa.String(150), nullable=False),
        sa.Column("status_description", sa.Text()),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source_system",
            sa.Enum(
                "portal", "processing_center", "biometrics_provider", "courier",
                name="source_system", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("location", sa.String(200)),
        sa.Column("visible_to_applicant", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"], ["visa_applications.application_id"],
            ondelete="CASCADE",
            name="fk_application_status_history_application_id_visa_applications",
        ),
    )
    op.create_index(
        "ix_application_status_history_application_time",
        "application_status_history",
        ["application_id", "event_timestamp"],
    )

    op.create_table(
        "appointments",
        sa.Column("appointment_id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), nullable=False),
        sa.Column(
            "appointment_type",
            sa.Enum(
                "biometrics", "interview", "document_submission",
                name="appointment_type", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("appointment_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("appointment_location", sa.String(200), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "scheduled", "completed", "cancelled", "rescheduled", "missed",
                name="appointment_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("rescheduled_from", sa.String(36)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "completed_at IS NULL OR completed_at >= appointment_date",
            name="ck_appointments_completion_after_appointment",
        ),
        sa.ForeignKeyConstraint(
            ["application_id"], ["visa_applications.application_id"],
            ondelete="CASCADE", name="fk_appointments_application_id_visa_applications",
        ),
        sa.ForeignKeyConstraint(
            ["rescheduled_from"], ["appointments.appointment_id"],
            ondelete="SET NULL", name="fk_appointments_rescheduled_from_appointments",
        ),
    )
    op.create_index(
        "ix_appointments_application_id", "appointments", ["application_id"]
    )

    op.create_table(
        "biometric_events",
        sa.Column("biometric_event_id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), nullable=False),
        sa.Column("appointment_id", sa.String(36)),
        sa.Column(
            "collection_status",
            sa.Enum(
                "pending", "collected", "failed",
                name="collection_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("collected_at", sa.DateTime(timezone=True)),
        sa.Column(
            "processing_status",
            sa.Enum(
                "pending", "in_progress", "completed", "failed",
                name="processing_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"], ["visa_applications.application_id"],
            ondelete="CASCADE",
            name="fk_biometric_events_application_id_visa_applications",
        ),
        sa.ForeignKeyConstraint(
            ["appointment_id"], ["appointments.appointment_id"],
            ondelete="SET NULL", name="fk_biometric_events_appointment_id_appointments",
        ),
    )
    op.create_index(
        "ix_biometric_events_application_id", "biometric_events", ["application_id"]
    )

    op.create_table(
        "application_documents",
        sa.Column("document_id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column(
            "submission_status",
            sa.Enum(
                "not_submitted", "requested", "submitted",
                name="document_submission_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column(
            "verification_status",
            sa.Enum(
                "not_reviewed", "pending", "verified", "rejected",
                name="verification_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("requested_again", sa.Boolean(), nullable=False),
        sa.Column("request_reason", sa.Text()),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"], ["visa_applications.application_id"],
            ondelete="CASCADE",
            name="fk_application_documents_application_id_visa_applications",
        ),
    )
    op.create_index(
        "ix_application_documents_application_id",
        "application_documents",
        ["application_id"],
    )

    op.create_table(
        "additional_document_requests",
        sa.Column("request_id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True)),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column(
            "status",
            sa.Enum(
                "open", "submitted", "accepted", "closed", "overdue",
                name="document_request_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("instructions", sa.Text()),
        sa.CheckConstraint(
            "due_date IS NULL OR due_date >= requested_at",
            name="ck_additional_document_requests_due_after_request",
        ),
        sa.CheckConstraint(
            "submitted_at IS NULL OR submitted_at >= requested_at",
            name="ck_additional_document_requests_submission_after_request",
        ),
        sa.ForeignKeyConstraint(
            ["application_id"], ["visa_applications.application_id"],
            ondelete="CASCADE",
            name="fk_additional_document_requests_application_id_visa_applications",
        ),
    )
    op.create_index(
        "ix_additional_document_requests_application_id",
        "additional_document_requests", ["application_id"],
    )

    op.create_table(
        "application_decisions",
        sa.Column("decision_id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), nullable=False),
        sa.Column(
            "decision_type",
            sa.Enum(
                "granted", "refused", "withdrawn", "void",
                name="decision_type", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("decision_date", sa.Date(), nullable=False),
        sa.Column("decision_summary", sa.Text()),
        sa.Column("refusal_reason_category", sa.String(100)),
        sa.Column("appeal_available", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "(decision_type = 'refused' AND refusal_reason_category IS NOT NULL) "
            "OR decision_type != 'refused'",
            name="ck_application_decisions_refusal_has_reason_category",
        ),
        sa.ForeignKeyConstraint(
            ["application_id"], ["visa_applications.application_id"],
            ondelete="CASCADE",
            name="fk_application_decisions_application_id_visa_applications",
        ),
    )
    op.create_index(
        "ix_application_decisions_application_id",
        "application_decisions",
        ["application_id"],
    )

    op.create_table(
        "passport_tracking",
        sa.Column("tracking_id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), nullable=False),
        sa.Column("passport_received_at", sa.DateTime(timezone=True)),
        sa.Column("passport_dispatched_at", sa.DateTime(timezone=True)),
        sa.Column("courier_name", sa.String(150)),
        sa.Column("tracking_number", sa.String(100)),
        sa.Column(
            "delivery_status",
            sa.Enum(
                "awaiting_receipt", "received", "dispatched", "in_transit",
                "ready_for_collection", "delivered", "collected",
                name="delivery_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "passport_dispatched_at IS NULL OR passport_received_at IS NULL OR "
            "passport_dispatched_at >= passport_received_at",
            name="ck_passport_tracking_dispatch_after_receipt",
        ),
        sa.CheckConstraint(
            "delivered_at IS NULL OR passport_dispatched_at IS NULL OR "
            "delivered_at >= passport_dispatched_at",
            name="ck_passport_tracking_delivery_after_dispatch",
        ),
        sa.ForeignKeyConstraint(
            ["application_id"], ["visa_applications.application_id"],
            ondelete="CASCADE",
            name="fk_passport_tracking_application_id_visa_applications",
        ),
    )
    op.create_index(
        "ix_passport_tracking_application_id",
        "passport_tracking",
        ["application_id"],
    )


def downgrade() -> None:
    """Drop operational tables in reverse dependency order."""
    op.drop_table("passport_tracking")
    op.drop_table("application_decisions")
    op.drop_table("additional_document_requests")
    op.drop_table("application_documents")
    op.drop_table("biometric_events")
    op.drop_table("appointments")
    op.drop_table("application_status_history")
    op.drop_table("visa_applications")
    op.drop_table("users")
