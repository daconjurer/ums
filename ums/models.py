from typing import Any
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
import uuid


# Base data model


class Base(SQLModel):
    id: Any
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


# Associative tables (many-to-many relationships)


class UserGroupLink(Base, table=True):
    __tablename__ = "user_group_link"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
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
    verified_at: datetime | None = None
