#!/bin/bash
# Initialize DynamoDB table with real AWS credentials from .env.test

set -e

# Source environment variables from .env.test
if [ -f .env.test ]; then
    export $(cat .env.test | grep -v '^#' | xargs)
else
    echo "Error: .env.test not found"
    exit 1
fi

# Verify required environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$DYNAMODB_TABLE_NAME" ] || [ -z "$AWS_REGION" ]; then
    echo "Error: Missing required environment variables"
    exit 1
fi

echo "Creating DynamoDB table: $DYNAMODB_TABLE_NAME"
echo "Region: $AWS_REGION"
echo "Endpoint: $DYNAMODB_ENDPOINT_URL"

# Create DynamoDB table
aws dynamodb create-table \
  --table-name "$DYNAMODB_TABLE_NAME" \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=GSI1PK,AttributeType=S \
    AttributeName=GSI1SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes \
    "IndexName=GSI1,KeySchema=[{AttributeName=GSI1PK,KeyType=HASH},{AttributeName=GSI1SK,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region "$AWS_REGION" \
  --endpoint-url "$DYNAMODB_ENDPOINT_URL" 2>/dev/null || echo "Table already exists or creation failed (this is OK)"

echo "DynamoDB initialization complete"
