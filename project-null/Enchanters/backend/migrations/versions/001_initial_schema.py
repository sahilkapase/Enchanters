"""Initial schema - all KisaanSeva tables

Revision ID: 001_initial
Revises: None
Create Date: 2026-02-21

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    land_unit_enum = postgresql.ENUM("acre", "hectare", "bigha", name="land_unit_enum", create_type=False)
    land_unit_enum.create(op.get_bind(), checkfirst=True)

    season_enum = postgresql.ENUM("kharif", "rabi", "zaid", name="season_enum", create_type=False)
    season_enum.create(op.get_bind(), checkfirst=True)

    irrigation_type_enum = postgresql.ENUM("rainfed", "canal", "borewell", "drip", "sprinkler", name="irrigation_type_enum", create_type=False)
    irrigation_type_enum.create(op.get_bind(), checkfirst=True)

    ownership_type_enum = postgresql.ENUM("owned", "leased", "shared", name="ownership_type_enum", create_type=False)
    ownership_type_enum.create(op.get_bind(), checkfirst=True)

    doc_type_enum = postgresql.ENUM("aadhaar", "ration_card", "land_proof", "bank_passbook", "photo", name="doc_type_enum", create_type=False)
    doc_type_enum.create(op.get_bind(), checkfirst=True)

    benefit_type_enum = postgresql.ENUM("cash", "subsidy", "insurance", "equipment", name="benefit_type_enum", create_type=False)
    benefit_type_enum.create(op.get_bind(), checkfirst=True)

    rule_type_enum = postgresql.ENUM("crop", "land_min", "land_max", "state", "district", "season", "ownership", "irrigation", name="rule_type_enum", create_type=False)
    rule_type_enum.create(op.get_bind(), checkfirst=True)

    insurance_plan_type_enum = postgresql.ENUM("pmfby", "rwbci", "other", name="insurance_plan_type_enum", create_type=False)
    insurance_plan_type_enum.create(op.get_bind(), checkfirst=True)

    subsidy_category_enum = postgresql.ENUM("seed", "fertilizer", "equipment", "irrigation", "organic", "credit", name="subsidy_category_enum", create_type=False)
    subsidy_category_enum.create(op.get_bind(), checkfirst=True)

    reminder_type_enum = postgresql.ENUM("scheme", "subsidy", "insurance", name="reminder_type_enum", create_type=False)
    reminder_type_enum.create(op.get_bind(), checkfirst=True)

    reminder_channel_enum = postgresql.ENUM("sms", "whatsapp", "email", name="reminder_channel_enum", create_type=False)
    reminder_channel_enum.create(op.get_bind(), checkfirst=True)

    center_type_enum = postgresql.ENUM("csc", "jan_suvidha", "bank", "other", name="center_type_enum", create_type=False)
    center_type_enum.create(op.get_bind(), checkfirst=True)

    agent_session_status_enum = postgresql.ENUM("active", "expired", "ended", name="agent_session_status_enum", create_type=False)
    agent_session_status_enum.create(op.get_bind(), checkfirst=True)

    generated_by_type_enum = postgresql.ENUM("farmer", "agent", name="generated_by_type_enum", create_type=False)
    generated_by_type_enum.create(op.get_bind(), checkfirst=True)

    deadline_season_enum = postgresql.ENUM("kharif", "rabi", "zaid", name="deadline_season_enum", create_type=False)
    deadline_season_enum.create(op.get_bind(), checkfirst=True)

    # farmers
    op.create_table(
        "farmers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farmer_id", sa.String(11), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(15), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(255)),
        sa.Column("email_verified", sa.Boolean, server_default="false"),
        sa.Column("phone_verified", sa.Boolean, server_default="false"),
        sa.Column("pin_code", sa.String(6), nullable=False),
        sa.Column("district", sa.String(100)),
        sa.Column("state", sa.String(100)),
        sa.Column("land_area", sa.Numeric(10, 2), nullable=False),
        sa.Column("land_unit", land_unit_enum, server_default="acre"),
        sa.Column("language_pref", sa.String(10), server_default="hi"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # farmer_profiles
    op.create_table(
        "farmer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("aadhaar_masked", sa.String(8)),
        sa.Column("ration_card_no", sa.String(20)),
        sa.Column("bank_account", sa.String(255)),
        sa.Column("bank_ifsc", sa.String(11)),
        sa.Column("irrigation_type", irrigation_type_enum),
        sa.Column("ownership_type", ownership_type_enum),
    )

    # farmer_crops
    op.create_table(
        "farmer_crops",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("crop_name", sa.String(100), nullable=False),
        sa.Column("season", season_enum, nullable=False),
        sa.Column("year", sa.String(4), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )

    # farmer_documents
    op.create_table(
        "farmer_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doc_type", doc_type_enum, nullable=False),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("verified", sa.Boolean, server_default="false"),
    )

    # schemes
    op.create_table(
        "schemes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name_en", sa.String(300), nullable=False),
        sa.Column("name_hi", sa.String(300)),
        sa.Column("ministry", sa.String(200)),
        sa.Column("description_en", sa.Text),
        sa.Column("description_hi", sa.Text),
        sa.Column("benefit_type", benefit_type_enum, nullable=False),
        sa.Column("benefit_amount", sa.String(100)),
        sa.Column("apply_url", sa.String(500)),
        sa.Column("documents_required", postgresql.JSONB, server_default="[]"),
        sa.Column("how_to_apply", sa.Text),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("source_url", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # scheme_eligibility
    op.create_table(
        "scheme_eligibility",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scheme_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_type", rule_type_enum, nullable=False),
        sa.Column("rule_value", sa.String(200), nullable=False),
        sa.Column("is_mandatory", sa.Boolean, server_default="true"),
    )

    # scheme_deadlines
    op.create_table(
        "scheme_deadlines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scheme_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("season", deadline_season_enum),
        sa.Column("year", sa.Integer),
        sa.Column("open_date", sa.Date),
        sa.Column("close_date", sa.Date),
        sa.Column("state", sa.String(100)),
    )

    # insurance_plans
    op.create_table(
        "insurance_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name_en", sa.String(300), nullable=False),
        sa.Column("name_hi", sa.String(300)),
        sa.Column("plan_type", insurance_plan_type_enum, nullable=False),
        sa.Column("description_en", sa.Text),
        sa.Column("description_hi", sa.Text),
        sa.Column("coverage", sa.Text),
        sa.Column("premium_info", sa.Text),
        sa.Column("eligibility", sa.Text),
        sa.Column("how_to_enroll", sa.Text),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )

    # subsidies
    op.create_table(
        "subsidies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name_en", sa.String(300), nullable=False),
        sa.Column("name_hi", sa.String(300)),
        sa.Column("category", subsidy_category_enum, nullable=False),
        sa.Column("description_en", sa.Text),
        sa.Column("description_hi", sa.Text),
        sa.Column("benefit_amount", sa.String(100)),
        sa.Column("eligibility", postgresql.JSONB, server_default="{}"),
        sa.Column("open_date", sa.Date),
        sa.Column("close_date", sa.Date),
        sa.Column("state", sa.String(100)),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )

    # reminders
    op.create_table(
        "reminders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", reminder_type_enum, nullable=False),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("remind_date", sa.Date, nullable=False),
        sa.Column("channel", reminder_channel_enum, nullable=False),
        sa.Column("sent", sa.Boolean, server_default="false"),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
    )

    # agents
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(15), unique=True, nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("center_name", sa.String(200)),
        sa.Column("center_type", center_type_enum),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # agent_sessions
    op.create_table(
        "agent_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.String(300)),
        sa.Column("otp_verified_at", sa.DateTime(timezone=True)),
        sa.Column("session_start", sa.DateTime(timezone=True)),
        sa.Column("session_end", sa.DateTime(timezone=True)),
        sa.Column("forms_downloaded", postgresql.JSONB, server_default="[]"),
        sa.Column("actions_taken", postgresql.JSONB, server_default="[]"),
        sa.Column("status", agent_session_status_enum, server_default="active"),
    )

    # generated_forms
    op.create_table(
        "generated_forms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scheme_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schemes.id", ondelete="SET NULL")),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("generated_by", generated_by_type_enum, nullable=False),
        sa.Column("agent_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agent_sessions.id", ondelete="SET NULL")),
    )


def downgrade() -> None:
    op.drop_table("generated_forms")
    op.drop_table("agent_sessions")
    op.drop_table("agents")
    op.drop_table("reminders")
    op.drop_table("subsidies")
    op.drop_table("insurance_plans")
    op.drop_table("scheme_deadlines")
    op.drop_table("scheme_eligibility")
    op.drop_table("schemes")
    op.drop_table("farmer_documents")
    op.drop_table("farmer_crops")
    op.drop_table("farmer_profiles")
    op.drop_table("farmers")

    for enum_name in [
        "generated_by_type_enum", "agent_session_status_enum", "center_type_enum",
        "reminder_channel_enum", "reminder_type_enum", "subsidy_category_enum",
        "insurance_plan_type_enum", "rule_type_enum", "benefit_type_enum",
        "doc_type_enum", "ownership_type_enum", "irrigation_type_enum",
        "deadline_season_enum", "season_enum", "land_unit_enum",
    ]:
        postgresql.ENUM(name=enum_name).drop(op.get_bind(), checkfirst=True)
