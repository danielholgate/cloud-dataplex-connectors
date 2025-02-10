"""Reads Mysql using PySpark."""
from typing import Dict
from pyspark.sql import SparkSession, DataFrame

from src.constants import EntryType

SPARK_JAR_PATH = "/opt/spark/jars/mysql-connector-j-9.2.0.jar"

class MysqlConnector:
    """Reads data from Mysql and returns Spark Dataframes."""

    def __init__(self, config: Dict[str, str]):
        # PySpark entrypoint
        self._spark = SparkSession.builder.appName("OracleIngestor") \
            .config("spark.jars", SPARK_JAR_PATH) \
            .getOrCreate()

        self._config = config
        # Use correct JDBC connection string depending on Service vs SID
        self._url = f"jdbc:mysql://{config['host']}:{config['port']}/{config['database']}?zeroDateTimeBehavior=CONVERT_TO_NULL&useSSL=false"

    def _execute(self, query: str) -> DataFrame:
        """A generic method to execute any query."""
        return self._spark.read.format("jdbc") \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .option("url", self._url) \
            .option("query", query) \
            .option("user", self._config["user"]) \
            .option("password", self._config["password"]) \
            .load()

    def get_db_schemas(self) -> DataFrame:
        """In Mysql, schemas are the databases."""
        query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA where SCHEMA_NAME = '{self._config['database']}'"
        return self._execute(query)

    def _get_columns(self, schema_name: str, object_type: str) -> str:
        """Gets a list of columns in tables or views in a batch."""
        # Every line here is a column that belongs to the table or to the view.
        # This SQL gets data from ALL the tables in a given schema.
        return (f"SELECT TABLE_NAME, COLUMN_NAME, "
                f"COLUMN_TYPE, IS_NULLABLE "
                f"FROM INFORMATION_SCHEMA.COLUMNS "
                f"WHERE TABLE_SCHEMA = '{schema_name}' "
                f"AND TABLE_TYPE = '{object_type}'")

    def get_dataset(self, schema_name: str, entry_type: EntryType):
        """Gets data for a table or a view."""
        # Dataset means that these entities can contain end user data.
        short_type =  'BASE TABLE' if entry_type.name == 'TABLE' else 'VIEW' # table or view, or the title of enum value
        query = self._get_columns(schema_name, short_type)
        return self._execute(query)
