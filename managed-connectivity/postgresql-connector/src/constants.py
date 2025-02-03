"""Constants that are used in the different files."""
import enum

SOURCE_TYPE = "postgres"

# Symbols for replacement
FORBIDDEN = "#"
ALLOWED = "!"


class EntryType(enum.Enum):
    """Types of Postgres entries."""
    INSTANCE: str = "projects/{project}/locations/{location}/entryTypes/postgres-instance"
    DATABASE: str = "projects/{project}/locations/{location}/entryTypes/postgres-database"
    DB_SCHEMA: str = "projects/{project}/locations/{location}/entryTypes/postgres-schema"
    TABLE: str = "projects/{project}/locations/{location}/entryTypes/postgres-table"
    VIEW: str = "projects/{project}/locations/{location}/entryTypes/postgres-view"
