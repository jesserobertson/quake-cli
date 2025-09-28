"""
CAP (Common Alerting Protocol) models for GeoNet API responses.

This module provides Pydantic models for parsing CAP alerts from the GeoNet API,
including Atom feed entries and individual CAP XML documents.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CapEntry(BaseModel):
    """A single CAP entry from the Atom feed."""

    id: str
    title: str
    updated: datetime
    published: datetime
    summary: str | None = None
    link: str | None = None
    author: str | None = None

    @classmethod
    def from_atom_entry(cls, entry_data: dict[str, Any]) -> "CapEntry":
        """Create a CapEntry from Atom feed XML data."""
        return cls(
            id=entry_data.get("id", ""),
            title=entry_data.get("title", ""),
            updated=datetime.fromisoformat(
                entry_data.get("updated", "").replace("Z", "+00:00")
            ),
            published=datetime.fromisoformat(
                entry_data.get("published", "").replace("Z", "+00:00")
            ),
            summary=entry_data.get("summary"),
            link=entry_data.get("link", {}).get("@href")
            if entry_data.get("link")
            else None,
            author=entry_data.get("author", {}).get("name")
            if entry_data.get("author")
            else None,
        )


class CapFeed(BaseModel):
    """CAP feed response containing multiple CAP entries."""

    id: str
    title: str
    updated: datetime
    author_name: str | None = None
    author_email: str | None = None
    author_uri: str | None = None
    entries: list[CapEntry] = Field(default_factory=list)

    @classmethod
    def from_atom_feed(cls, feed_data: dict[str, Any]) -> "CapFeed":
        """Create a CapFeed from Atom feed XML data."""
        feed = feed_data.get("feed", {})

        # Parse author information
        author = feed.get("author", {})
        author_name = author.get("name") if author else None
        author_email = author.get("email") if author else None
        author_uri = author.get("uri") if author else None

        # Parse entries
        entries_data = feed.get("entry", [])
        if not isinstance(entries_data, list):
            entries_data = [entries_data] if entries_data else []

        entries = [CapEntry.from_atom_entry(entry) for entry in entries_data]

        return cls(
            id=feed.get("id", ""),
            title=feed.get("title", ""),
            updated=datetime.fromisoformat(
                feed.get("updated", "").replace("Z", "+00:00")
            ),
            author_name=author_name,
            author_email=author_email,
            author_uri=author_uri,
            entries=entries,
        )

    @property
    def count(self) -> int:
        """Total number of CAP entries in the feed."""
        return len(self.entries)


class CapAlert(BaseModel):
    """Individual CAP alert document."""

    identifier: str
    sender: str
    sent: datetime
    status: str
    msg_type: str = Field(alias="msgType")
    scope: str
    code: list[str] = Field(default_factory=list)
    note: str | None = None
    references: str | None = None
    incidents: str | None = None
    info: list[dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def from_cap_xml(cls, cap_data: dict[str, Any]) -> "CapAlert":
        """Create a CapAlert from CAP XML data."""
        alert = cap_data.get("alert", {})

        return cls(
            identifier=alert.get("identifier", ""),
            sender=alert.get("sender", ""),
            sent=datetime.fromisoformat(alert.get("sent", "").replace("Z", "+00:00")),
            status=alert.get("status", ""),
            msgType=alert.get("msgType", ""),
            scope=alert.get("scope", ""),
            code=alert.get("code", [])
            if isinstance(alert.get("code"), list)
            else [alert.get("code", "")],
            note=alert.get("note"),
            references=alert.get("references"),
            incidents=alert.get("incidents"),
            info=alert.get("info", [])
            if isinstance(alert.get("info"), list)
            else [alert.get("info", {})]
            if alert.get("info")
            else [],
        )
