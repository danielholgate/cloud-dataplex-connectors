"""Reads PostgreSQL using PySpark."""
from typing import Dict
from pyspark.sql import SparkSession, DataFrame

from src.constants import EntryType


SPARK_JAR_PATH = "/opt/spark/jars/postgresql-42.6.0.jar"


class PostgresConnector:
    """Reads data from PostgreSQL and returns Spark Dataframes."""

    def __init__(self, config: Dict[str, str]):
        # PySpark entrypoint
        self._spark = SparkSession.builder.appName("PostgresIngestor") \
            .config("spark.jars", SPARK_JAR_PATH) \
            .getOrCreate()

        self._config = config
        self._url = f"jdbc:postgresql://{config['host']}:{config['port']}/{config['database']}"

    def _execute(self, query: str) -> DataFrame:
        """A generic method to execute any query."""
        return self._spark.read.format("jdbc") \
            .option("driver", "org.postgresql.Driver") \
            .option("url", self._url) \
            .option("query", query) \
            .option("user", self._config["user"]) \
            .option("password", self._config["password"]) \
            .load()

    def get_db_schemas(self) -> DataFrame:
        """Gets a list of schemas in the database."""
        query = "SELECT DISTINCT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema') AND schema_name NOT LIKE 'pg_toast%'"
        return self._execute(query)

    def _get_columns(self, schema_name: str, object_type: str) -> str:
        """Gets a list of columns in tables or views in a batch."""
        return (f"""SELECT 
                        t.relname as table_name, 
                        a.attname as column_name, 
                        ty.typname as data_type, 
                        a.attnotnull as is_nullable 
                    FROM 
                        pg_class t 
                        JOIN pg_namespace ns ON t.relnamespace = ns.oid 
                        JOIN pg_attribute a ON t.oid = a.attrelid 
                        JOIN pg_type ty ON a.atttypid = ty.oid 
                    WHERE 
                        ns.nspname = '{schema_name}' 
                        AND t.relkind = '{object_type}' 
                        AND a.attnum > 0
                """)
        

    def get_dataset(self, schema_name: str, entry_type: EntryType):
        """Gets data for a table or a view."""
        # Dataset means that these entities can contain end user data.
        if entry_type == EntryType.TABLE:
            object_type = 'r' # PostgreSQL code for regular table
        elif entry_type == EntryType.VIEW:
            object_type = 'v' # PostgreSQL code for view
        else:
            raise ValueError(f"Unsupported entry type: {entry_type}")
        query = self._get_columns(schema_name, object_type)
        return self._execute(query)
