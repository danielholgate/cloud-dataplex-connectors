# SQL Server Connector

This connector imports metadata from SQL Server databases into Google Cloud Dataplex.

## Preparing your SQL Server environment:

1. **Create a user** in the SQL Server instance(s) which will be used by Dataplex to connect and extract metadata about tables and views. The user requires the following permissions:
   * **CONNECT to the database**
   * **VIEW DEFINITION** on the tables and views you want to extract metadata from.
   * Alternatively, grant the user the **db_datareader** role for broader access. 

2. **Add the password** for the user to the Google Cloud Secret Manager in your project and note the ID (format: projects/[project-id]/secrets/[secret-name]).

## Running the connector locally:

1. **Install Python and pip:** Ensure you have Python 3.6 or later and pip installed on your system.

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt

3. **Run the connector:**
   ```bash
   python3 main.py \
   --target_project_id [your_gcp_project] \
   --target_location_id us-central1 \
   --target_entry_group_id <your-dataplex-entry-group-id> \
   --host <your-sql-server-host> \
   --port <your-sql-server-port> \
   --user <your-sql-server-user> \
   --password-secret <your-secret-resource-name> \
   --database <your-sql-server-database> \
   --output_bucket <your-output-gcs-bucket> \
   --output_folder <your-output-gcs-folder>


## Build a container image and run the connector with Dataproc Serverless (Allows extraction jobs to be scheduled):

1. **Build the Docker image:**
   ```bash
   docker build -t <your-image-name> .

2. **Push the image to Google Container Registry:**
   ```bash
   docker tag <your-image-name> gcr.io/<your-gcp-project>/<your-image-name>
   docker push gcr.io/<your-gcp-project>/<your-image-name>

3. **Create a bucket** which will be used for Dataproc to store temporary artifacts as it works (`--deps-bucket` parameter below).

4. **Run the connector on Dataproc Serverless:**
   ```bash
   gcloud dataproc batches submit pyspark \
   --project=<your-gcp-project> \
   --region=<your-gcp-location> \
   --batch=<your-batch-id> \
   --deps-bucket=<depencies-bucket-for-dataproc> \
   --container-image=gcr.io/<your-gcp-project>/<your-image-name> \
   --service-account=<your-service-account> \
   --network=<your-network-name> \
   main.py \
   --target_project_id <your-gcp-project> \
   --target_location_id <your-gcp-location> \
   --target_entry_group_id <your-entry-group-id> \
   --host <your-sql-server-host> \
   --port <your-sql-server-port> \
   --user <your-sql-server-user> \
   --password-secret <your-secret-resource-name> \
   --database <your-sql-server-database> \
   --output_bucket <your-output-gcs-bucket> \
   --output_folder <your-output-gcs-folder>