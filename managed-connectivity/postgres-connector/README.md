# PostgreSQL Connector

This connector imports metadata from PostgreSQL databases into Google Cloud Dataplex.

## Prepare your PostgreSQL environment:

1. Create a user in the PostgreSQL instance(s) which will be used by Dataplex to connect and extract metadata about tables and views. The user requires the following PostgreSQL privileges:
    * CONNECT to the database
    * SELECT on pg_class, pg_namespace, pg_attribute, pg_type, information_schema.columns
    * USAGE on all relevant schemas for which metadata needs to be extracted
2. Add the password for the user to the Google Cloud Secret Manager in your project and note the ID (format: projects/[project-id]/secrets/[secret-name])

## Running the connector locally:

Run the connector to test metadata extraction to GCS.

1. Download **postgresql-42.6.0.jar** (or the version you prefer) from Maven repository 
2. Change the driver path in [source code](src/postgres_connector.py) to the location of the jar file
3. Ensure Java Runtime Environment (JRE) is installed in your environment
4. Install PySpark: `pip install pyspark`
5. Install all other dependencies from the requirements.txt file: `pip install -r requirements.txt`
6. Run the connector. Example:

```shell
python3 main.py \
--target_project_id my-gcp-project \
--target_location_id us-central1 \
--target_entry_group_id XXX \
--host the-postgres-server \
--port 5432 \
--user dataplexagent \
--password-secret projects/73813454526/dataplexagent_postgres \
--database my_database \
--output_bucket gs://dataplex_connectivity_imports \
--output_folder=postgres

## Build a container image and run the connector with Dataproc Serverless:

Run the connector to test metadata extraction to GCS.

1. Run the script `bash build_and_push_docker.sh`. Registry build process will initially take up to 10 mins.
2. Upload the **postgresql-42.6.0.jar** to a Google Cloud storage location (add path to --jars parameter below)
3. Create a bucket which will be used for Dataproc to store temporary artifacts as it works (--deps-bucket parameter below)
4. To run the connector execute the following (substituting appropriate values for your environment):

```shell
gcloud dataproc batches submit pyspark \
    --project=my-gcp-project \
    --region=us-central1 \
    --batch=0001 \
    --deps-bucket=dataplex-metadata-collection-usc1 \ 
    --container-image=us-central1-docker.pkg.dev/daniel-dataplex/docker-repo/postgres-pyspark@sha256:dab02ca02f60a9e12767996191b06d859b947d89490d636a34fc734d4a0b6d08 \
    --service-account=440165342669-compute@developer.gserviceaccount.com \
    --jars=[gs://path/to/postgresql-42.6.0.jar] \
    --network=[Your-Network-Name] \
    main.py \
--  --target_project_id daniel-dataplex \
      --target_location_id us-central1 \
      --target_entry_group_id XXX \
      --host the-postgres-server \
      --port 5432 \
      --user dataplexagent \
      --password-secret projects/73813454526/dataplexagent_postgres \
      --database my_database \
      --output_bucket gs://dataplex_connectivity_imports \
      --output_folder postgres
