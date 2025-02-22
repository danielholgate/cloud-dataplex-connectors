"""Constants that are used in the different files."""
import enum

SOURCE_TYPE = "mysql"

# Symbols for replacement
FORBIDDEN = "#"
ALLOWED = "!"


class EntryType(enum.Enum):
    """Types of Mysql entries."""
    INSTANCE: str = "projects/{project}/locations/{location}/entryTypes/mysql-instance"
    DATABASE: str = "projects/{project}/locations/{location}/entryTypes/mysql-database"
    ##DB_SCHEMA: str = "projects/{project}/locations/{location}/entryTypes/mysql-schema"
    TABLE: str = "projects/{project}/locations/{location}/entryTypes/mysql-table"
    VIEW: str = "projects/{project}/locations/{location}/entryTypes/mysql-view"
