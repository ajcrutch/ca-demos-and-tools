#!/bin/bash
set -e

# Default Configuration
PROJECT_ID=${PROJECT_ID:-"ca-agent-ops-prism-dev"}
REGION=${REGION:-"us-central1"}
IMAGE_NAME=${IMAGE_NAME:-"prism-app"}
REPO_NAME=${REPO_NAME:-"cr-images"}
CLOUDSQL_INSTANCE="ca-agent-ops-prism-dev:us-central1:prism-prod"

# Prism Core Environment Variables
PRISM_GDA_PROJECTS=${PRISM_GDA_PROJECTS:-"ca-agent-ops-prism-dev"}
PRISM_GENAI_CLIENT_PROJECT=${PRISM_GENAI_CLIENT_PROJECT:-"ca-agent-ops-prism-dev"}
PRISM_GENAI_CLIENT_LOCATION=${PRISM_GENAI_CLIENT_LOCATION:-"global"}

# Create Artifact Registry repository if it doesn't exist
# gcloud artifacts repositories create cr-images \
#   --repository-format=docker \
#   --location=us-central1 \
#   --description="Docker repository for Prism app images" \
#   --project=ca-agent-ops-prism-dev
SERVICE_ACCOUNT=${SERVICE_ACCOUNT:-"161716129226-compute@developer.gserviceaccount.com"}

# Corp Run Network Configuration
VPC_NETWORK=${VPC_NETWORK:-"cr-infra-vpc-network"}
VPC_SUBNET=${VPC_SUBNET:-"cr-infra-subnetwork"}

# Constructed Image URL
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest"

echo "========================================================"
echo "Deploying Prism App to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "Image:   $IMAGE_URL"
echo "========================================================"

# 1. Build the Image
echo " Building Docker image..."
gcloud builds submit \
  --tag "$IMAGE_URL" \
  --project="$PROJECT_ID" \
  .

# 2. Deploy to Cloud Run
echo " Deploying to Cloud Run..."
gcloud run deploy "$IMAGE_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="$IMAGE_URL" \
  --ingress=internal-and-cloud-load-balancing \
  --service-account="$SERVICE_ACCOUNT" \
  --cpu=2 \
  --memory=4Gi \
  --network="$VPC_NETWORK" \
  --subnet="$VPC_SUBNET" \
  --vpc-egress=all-traffic \
  --execution-environment=gen2 \
  --add-cloudsql-instances="$CLOUDSQL_INSTANCE" \
  --set-env-vars="INSTANCE_CONNECTION_NAME=$CLOUDSQL_INSTANCE,DB_USER=postgres,DB_NAME=prism,DB_IP_TYPE=PRIVATE,PRISM_GDA_PROJECTS=$PRISM_GDA_PROJECTS,PRISM_GENAI_CLIENT_PROJECT=$PRISM_GENAI_CLIENT_PROJECT,PRISM_GENAI_CLIENT_LOCATION=$PRISM_GENAI_CLIENT_LOCATION" \
  --set-secrets="DB_PASS=PRISM_PROD_DB_PASSWORD:latest" \
  --concurrency=80

echo "========================================================"
echo "Deployment Complete!"
echo "Service URL:"
gcloud run services describe "$IMAGE_NAME" --project="$PROJECT_ID" --region="$REGION" --format='value(status.url)'
echo "========================================================"
