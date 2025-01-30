# Oracle Connector

This custom connector exports metadata for tables and views from Oracle databases to create a [metadata import file](https://cloud.google.com/dataplex/docs/import-metadata#components) which can be imported into Google Dataplex. 
You can read more about custom connectors in the documentation for [Dataplex Managed Connectivity framework](https://cloud.google.com/dataplex/docs/managed-connectivity-overview) and [Developing a custom connector](https://cloud.google.com/dataplex/docs/develop-custom-connector) for Dataplex.

## Prepare your Oracle environment:

1. Create a user in the Oracle instance(s) which will be used by Dataplex to connect and extract metadata about tables and views. The user requires at minimum the following Oracle privileges and roles: 
    * CONNECT and CREATE SESSION
    * SELECT on DBA_OBJECTS
    * SELECT on all schemas for which metadata needs to be extracted
2. Add the password for the user to the Google Cloud Secret Manager in your project and note the Secret ID (format is: projects/[project-number]/secrets/[secret-name])

### Parameters
The Oracle connector takes the following parameters:
|Parameter|Description|Mandatory/Optional|
|---------|------------|-------------|
|target_project_id|GCP Project ID/Project Number or 'global'. Used in the generated Dataplex Entry, Aspects and AspectTypes|MANDATORY|
|target_location_id|GCP Region ID or 'global'. Used in the generated Dataplex Entry, Aspects and AspectTypes|MANDATORY|
|target_entry_group_id|Dataplex Entry Group ID to use in the generated data|MANDATORY|
|host|Oracle server to connect to|MANDATORY|
|port|Oracle Server port (usually 1521)|MANDATORY|
|service|Oracle service to connect to. Either service or sid must be specified|OPTIONAL
|sid|Oracle SID (Service Identifier). Either service or sid must be specified|OPTIONAL
|user|Username to connect with|MANDATORY|
|password-secret|GCP Secret Manager ID holding the password for the user. Format: projects/[PROJ]/secrets/[SECRET]|MANDATORY|
|output_bucket|GCS bucket where the output file will be stored|MANDATORY|
|output_folder|Folder within the GCS bucket where the export output file will be stored|MANDATORY|

### Running the connector
There are three ways to run the connector:
1) [Run the script directly from the command line](###running-from-the-command-line) (extract metadata into GCS)
2) [Run as a container via a Dataproc Serverless job](###submitting-a-metadata-extraction-job-to-dataproc-serverless) (extract metadata into GCS)
3) [Schedule and run as a container via Workflows](###schedule-an-end-to-end-metadata-extract-and-import-with-workflows) ] (End-to-end. Extract metadata into GCS and import metadata into Dataplex)

#### Running from the command line

The metadata connector can be run ad-hoc from the command line for development or testing by directly executing the main.py script.

### Prepare the environment:
1. Download **ojdbc11.jar** [from Oracle](https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html)
2. Edit the SPARK_JAR_PATH variable in [oracle_connector.py](src/oracle_connector.py) to match the location of the jar file
3. Ensure a Java Runtime Environment (JRE) is installed in your environment
4. Install PySpark: `pip3 install pyspark`
5. Install all dependencies from the requirements.txt file with `pip3 install -r requirements.txt`

### Required IAM Roles
- roles/secretmanager.secretAccessor
- roles/storage.objectUser

Before you run the script ensure you session is authenticated as a user which has these roles at minimum (ie using ```gcloud auth application-default login```)

To execute the metadata extraction run the following command (substituting appropriate values for your environment):

```shell 
python3 main.py \
--target_project_id my-gcp-project-id \
--target_location_id us-central1 \
--target_entry_group_id oracledbs \
--host the-oracle-server \
--port 1521 \
--user dataplexagent \
--password-secret projects/73813454526/dataplexagent_oracle \
--service XEPDB1 \
--output_bucket dataplex_connectivity_imports \
--output_folder oracle
```

### Output:
The connector generates a metadata extract in JSONL format as described [in the documentation](https://cloud.google.com/dataplex/docs/import-metadata#metadata-import-file). A sample output from the connector can be found [here](sample/oracle_output_sample.jsonl)

## Build a container and extract metadata as a [Dataproc Serverless](https://cloud.google.com/dataproc-serverless/docs) job:

To build a Docker container for the connector (one-time task) and run the extraction process as a Dataproc Serverless job:

### Build the container
1. Run the script ```build_and_push_docker.sh``` to build the Docker container and store it in Artifact Registry. This process can take take up to 10 minutes.
2. Upload the **odjcb11.jar** file to a Google Cloud Storage location (add this path to the **--jars** parameter below)
3. Create a GCS bucket which will be used for Dataproc Serverless as a working directory (add to the **--deps-bucket** parameter below)

### Submitting a metadata extraction job to Dataproc serverless:
Once the container is built you can run the metadata extract with the following command (substituting appropriate values for your environment). 

Note the service account you submit for the job with --service-account needs the following roles:

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
    --container-image=us-central1-docker.pkg.dev/my-gcp-project-id/docker-repo/oracle-pyspark@sha256:dab02ca02f60a9e12767996191b06d859b947d89490d636a34fc734d4a0b6d08 \
    --service-account=440165342669-compute@developer.gserviceaccount.com \
    --jars=[gs://path/to/ojdbc11.jar  \
    --network=[Your-Network-Name] \
    main.py \
--  --target_project_id my-gcp-project-id \
      --target_location_id us-central1	\
      --target_entry_group_id XXX \
      --host the-oracle-server \
      --port 1521 \
      --user dataplexagent \
      --password-secret projects/73813454526/dataplexagent_oracle \
      --service XEPDB1 \
      --output_bucket gs://dataplex_connectivity_imports \
      --output_folder oracle
```

## Schedule an end-to-end meatdata extraction and import with Workflows

To run an end-to-end metadata extraction and import process, run the container via Google Workflows. 

Follow the Dataplex documentation here: [Import metadata from a custom source using Workflows ](https://cloud.google.com/dataplex/docs/import-using-workflows-custom-source)


## Manually initiating a metadata import file into Dataplex

To import a metadata import file into Dataplex call the Import API with the following:

```http
POST https://dataplex.googleapis.com/v1/projects/PROJECT_NUMBER/locations/LOCATION_ID/metadataJobs?metadataJobId=METADATA_JOB_ID
```

See the [Dataplex documetation](https://cloud.google.com/dataplex/docs/import-metadata#import-metadata) for full instructions about importing metadata.
