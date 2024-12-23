import sys
from datetime import datetime

if sys.version_info > (3, 11):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc

import uuid

from sqlalchemy.types import TIMESTAMP
from sqlmodel import Field, Relationship, SQLModel

# Base data model


class Base(SQLModel):
    id: uuid.UUID
    created_at: datetime = Field(  # type: ignore [call-overload]
        sa_type=TIMESTAMP(timezone=True), default=datetime.now(UTC)
    )
    updated_at: datetime = Field(  # type: ignore [call-overload]
        sa_type=TIMESTAMP(timezone=True), default=datetime.now(UTC)
    )
    deleted_at: datetime | None = Field(sa_type=TIMESTAMP(timezone=True), default=None)  # type: ignore [call-overload]


# Associative tables (many-to-many relationships)


class UserGroupLink(Base, table=True):
    __tablename__ = "user_group_link"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    group_id: uuid.UUID | None = Field(
        foreign_key="groups.id", primary_key=True, nullable=True
    )
    user_id: uuid.UUID | None = Field(
        foreign_key="users.id", primary_key=True, nullable=True
    )


class RolePermissionLink(Base, table=True):
    __tablename__ = "role_permission_link"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    permission_id: uuid.UUID | None = Field(
        default=None, foreign_key="permissions.id", primary_key=True
    )
    role_id: uuid.UUID | None = Field(
        default=None, foreign_key="roles.id", primary_key=True
    )


# Models tables


class Group(Base, table=True):
    __tablename__ = "groups"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    name: str = Field(index=True)
    location: str
    description: str | None = None
    members: list["User"] = Relationship(
        back_populates="groups",
        link_model=UserGroupLink,
    )
    is_active: bool = True
    is_deleted: bool = False


class Role(Base, table=True):
    __tablename__ = "roles"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    name: str = Field(nullable=False, index=True)
    description: str | None = None
    permissions: list["Permissions"] = Relationship(
        back_populates="roles",
        link_model=RolePermissionLink,
    )
    is_active: bool = True
    is_deleted: bool = False


class Permissions(Base, table=True):
    __tablename__ = "permissions"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    name: str = Field(nullable=False, index=True)
    description: str | None = None
    roles: list[Role] = Relationship(
        back_populates="permissions",
        link_model=RolePermissionLink,
    )
    is_active: bool = True
    is_deleted: bool = False


class User(Base, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    name: str = Field(nullable=False, index=True)
    full_name: str
    email: str
    password: str
    groups: list[Group] = Relationship(
        back_populates="members",
        link_model=UserGroupLink,
    )
    is_verified: bool = False
    is_active: bool = True
    is_deleted: bool = False
    role_id: uuid.UUID | None = Field(default=None, foreign_key="roles.id")
    verified_at: datetime | None = Field(sa_type=TIMESTAMP(timezone=True), default=None)  # type: ignore [call-overload]
