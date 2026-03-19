#!/usr/bin/env python3
import os
import sys
import time
import boto3
from botocore.exceptions import ClientError, ConnectionError

def wait_for_dynamodb(endpoint_url, max_retries=30, retry_delay=2):
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=endpoint_url,
        region_name='us-east-1',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy'
    )
    
    for attempt in range(max_retries):
        try:
            dynamodb.meta.client.describe_table(TableName='test')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"[{attempt + 1}/{max_retries}] DynamoDB is ready")
                return True
        except (ConnectionError, Exception) as e:
            print(f"[{attempt + 1}/{max_retries}] Waiting for DynamoDB... ({type(e).__name__})")
            time.sleep(retry_delay)
            continue
        
        print(f"[{attempt + 1}/{max_retries}] DynamoDB is ready")
        return True
    
    print("Failed to connect to DynamoDB after retries")
    return False

def create_table(endpoint_url):
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=endpoint_url,
        region_name='us-east-1',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy'
    )
    
    table_name = 'eisenhower-tasks'
    
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table '{table_name}' already exists")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceNotFoundException':
            print(f"Error checking table: {e}")
            return False
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1SK', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'GSI1',
                    'KeySchema': [
                        {'AttributeName': 'GSI1PK', 'KeyType': 'HASH'},
                        {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        table.wait_until_exists()
        print(f"Table '{table_name}' created successfully")
        return True
    except ClientError as e:
        print(f"Error creating table: {e}")
        return False

if __name__ == '__main__':
    endpoint_url = os.getenv('DYNAMODB_ENDPOINT_URL', 'http://localhost:8000')
    
    print(f"Connecting to DynamoDB at {endpoint_url}...")
    if not wait_for_dynamodb(endpoint_url):
        sys.exit(1)
    
    print("Creating DynamoDB table...")
    if not create_table(endpoint_url):
        sys.exit(1)
    
    print("DynamoDB initialization complete")
    sys.exit(0)
