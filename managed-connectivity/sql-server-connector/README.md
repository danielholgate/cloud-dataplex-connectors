# SQL Server Connector

This custom connector exports metadata for tables and views from SQL Server databases to create a [metadata import file](https://cloud.google.com/dataplex/docs/import-metadata#components) which can be imported into Google Dataplex. 
You can read more about custom connectors in the documentation for [Dataplex Managed Connectivity framework](https://cloud.google.com/dataplex/docs/managed-connectivity-overview) and [Developing a custom connector](https://cloud.google.com/dataplex/docs/develop-custom-connector) for Dataplex.

## Prepare your SQL Server environment:

1. Create a user in the SQL Server instance(s) which will be used by Dataplex to connect and extract metadata about tables and views. This user requires the following SQL Server permissions: 
    * CONNECT to the database
    * SELECT on all tables in the target database(s)
2. Add the password for the user to the Google Cloud Secret Manager in your project and note the Secret ID (format is: projects/[project-number]/secrets/[secret-name])

## Extract metadata by running the connector from the command line:

You can run the connector directly from the command line for testing or development purposes.

### Required IAM Roles
- roles/secretmanager.secretAccessor
- roles/storage.objectUser

Be sure to your session is authenticated as a user which has these roles at minimum (ie using ```gcloud auth application-default login```)

### Prepare the environment:
1. Download the **mssql-jdbc** jar file [from Microsoft](https://docs.microsoft.com/en-us/sql/connect/jdbc/download-microsoft-jdbc-driver-for-sql-server?view=sql-server-2022) and include in the same folder as the other python files for this connector
2. Edit the SPARK_JAR_PATH variable in [sqlserver_connector.py](src/sqlserver_connector.py) to match the location of the jar file
3. Ensure a Java Runtime Environment (JRE) is installed in your environment
4. Install PySpark: `pip3 install pyspark`
5. Install all dependencies from the requirements.txt file with `pip3 install -r requirements.txt`

### Running the metadata extraction
To execute a metadata extraction run the following command (substituting appropriate values for your environment):

```shell 
python3 main.py \
--target_project_id my-gcp-project-id \
--target_location_id us-central1 \
--target_entry_group_id sqlserverdbs \
--host the-sqlserver-server \
--port 1433 \
--user dataplexagent \
--password-secret projects/73813454526/dataplexagent_sqlserver \
--database AdventureWorksDW2019 \
--output_bucket dataplex_connectivity_imports \
--output_folder sqlserver
```

### Output:
The connector generates a metadata extract in JSONL format as described [in the documentation](https://cloud.google.com/dataplex/docs/import-metadata#metadata-import-file). A sample output from the connector can be found [here](sample/sqlserver_output_sample.jsonl)

## Build a container and extract metadata using [Dataproc Serverless](https://cloud.google.com/dataproc-serverless/docs)

To build a Docker container for the connector and run the extraction process as a Dataproc serverless job:

### Building the container
1. Run the script ```build_and_push_docker.sh``` to build the Docker container and store it in Artifact Registry. This process can take take up to 10 minutes.
2. Upload the **mssql-jdbc** jar file to a Google Cloud Storage location (add this path to the **--jars** parameter below)
3. Create a GCS bucket which will be used for Dataproc Serverless as a working directory (add to the **--deps-bucket** parameter below)

### Submitting a metadata extraction job to Dataproc serverless:
Once the container is built you can run the metadata extract with the following command (substituting appropriate values for your environment). 

The service account you submit for the job needs the following roles:

- roles/dataplex.catalogEditor
- roles/dataplex.entryGroupOwner
- roles/dataplex.metadataJobOwner
- roles/dataproc.admin
- roles/dataproc.editor
- roles/dataproc.worker
- roles/iam.serviceAccountUser
- roles/logging.logWriter
- roles/secretmanager.secretAccessor
- roles/workflows.invoker


```shell
gcloud dataproc batches submit pyspark \
    --project=my-gcp-project-id \
    --region=us-central1 \
    --batch=0001 \
    --deps-bucket=dataplex-metadata-collection-usc1 \  
    --container-image=us-central1-docker.pkg.dev/my-gcp-project-id/docker-repo/sqlserver-pyspark@sha256:dab02ca02f60a9e12767996191b06d859b947d89490d636a34fc734d4a0b6d08 \
    --service-account=440165342669-compute@developer.gserviceaccount.com \
    --jars=[gs://path/to/mssql-jdbc-9.4.1.jre8.jar]  \
    --network=[Your-Network-Name] \
    main.py \
--  --target_project_id my-gcp-project-id \
      --target_location_id us-central1	\
      --target_entry_group_id XXX \
      --host the-sqlserver-server \
      --port 1433 \
      --user dataplexagent \
      --password-secret projects/73813454526/dataplexagent_sqlserver \
      --database AdventureWorksDW2019 \
      --output_bucket gs://dataplex_connectivity_imports \
      --output_folder sqlserver
```

## Manually importing a metadata import file into Google Dataplex

To import a metadata import file into Dataplex call the Import API with the following:

```http
POST https://dataplex.googleapis.com/v1/projects/PROJECT_NUMBER/locations/LOCATION_ID/metadataJobs?metadataJobId=METADATA_JOB_ID

See the [Dataplex documetation](https://cloud.google.com/dataplex/docs/import-metadata#import-metadata) for full instructions about importing metadata.

## Run an end-to-end meatdata extraction and import process from SQL Server into Dataplex

To run an end-to-end metadata extraction and import process, run the container via Google Workflows. 

Follow the Dataplex documentation here: [Import metadata from a custom source using Workflows ](https://cloud.google.com/dataplex/docs/import-using-workflows-custom-source)
