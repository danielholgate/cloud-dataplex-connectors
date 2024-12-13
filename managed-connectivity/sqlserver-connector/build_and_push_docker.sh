```bash
#!/bin/bash

IMAGE=<your-image-name>:latest
PROJECT=<your-gcp-project>
REGION=<your-gcp-region>

REPO_IMAGE=gcr.io/${PROJECT}/${IMAGE}

docker build -t "${IMAGE}" .

# Tag and push to GCP container registry
gcloud config set project ${PROJECT}
gcloud auth configure-docker
docker tag "${IMAGE}" "${REPO_IMAGE}"
docker push "${REPO_IMAGE}"

