"""Command line reader."""

import argparse


def read_args():
    """Reads arguments from the command line."""
    parser = argparse.ArgumentParser()

    # Project arguments
    parser.add_argument("--target_project_id", type=str, required=True,
        help="The name of the target Google Cloud project to import the metadata into.")
    parser.add_argument("--target_location_id", type=str, required=True,
        help="The target Google Cloud location where the metadata will be imported into.")
    parser.add_argument("--target_entry_group_id", type=str, required=True,
        help="The ID of the Dataplex Entry Group to import metadata into. "
             "Metadata will be imported into entry group with the following"
             "full resource name: projects/${target_project_id}/"
             "locations/${target_location_id}/entryGroups/${target_entry_group_id}.")

    # SQL Server specific arguments
    parser.add_argument("--host", type=str, required=True,
        help="The SQL Server host server")
    parser.add_argument("--port", type=str, required=True,
        help="The port number (usually 1433)")
    parser.add_argument("--user", type=str, required=True, help="SQL Server User")
    parser.add_argument("--password-secret", type=str, required=True,
        help="Resource name in the Google Cloud Secret Manager for the SQL Server password")
    parser.add_argument("--instancename", type=str,required=False,
        help="The name of the SQL Server database to extract metadata from")
    parser.add_argument("--database", type=str,required=True,
        help="Databases")

    # Google Cloud Storage arguments
    # It is assumed that the bucket is in the same region as the entry group
    parser.add_argument("--output_bucket", type=str, required=True,
        help="The Cloud Storage bucket to write the generated metadata import file. Format begins with gs:// ")
    parser.add_argument("--output_folder", type=str, required=True,
        help="The folder within the Cloud Storage bucket, to write the generated metadata import files. Name only required")

    # Development arguments
    parser.add_argument("--testing", type=str, required=False,
    help="Test mode")
    
    return vars(parser.parse_known_args()[0])
