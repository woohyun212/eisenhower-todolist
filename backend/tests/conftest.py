"""Pytest configuration and shared fixtures for backend tests."""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.core.config import settings
from app.main import app


# ============================================================================
# DynamoDB Fixtures
# ============================================================================


@pytest.fixture
def dynamodb_table():
    """Create a mocked DynamoDB table for testing.
    
    Uses moto @mock_aws decorator to mock AWS services.
    Creates the 'eisenhower-tasks' table with:
    - PK: 'PK' (String)
    - SK: 'SK' (String)
    - GSI1: 'GSI1PK' (String), 'GSI1SK' (String)
    """
    with mock_aws():
        # Create DynamoDB resource (moto handles endpoint internally)
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        # Create table with PK, SK, and GSI1
        table = dynamodb.create_table(
            TableName=settings.DYNAMODB_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                }
            ],
            BillingMode="PROVISIONED",
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )

        yield table


# ============================================================================
# AI Client Fixtures
# ============================================================================


@pytest.fixture
def mock_ai_client():
    """Mock OpenAI client for AI service testing.
    
    Returns a MagicMock that simulates OpenAI API responses.
    Can be configured to return predefined JSON or raise errors.
    """
    mock_client = MagicMock()

    # Default successful response
    def default_response(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "urgency": "urgent",
                            "importance": "important",
                            "confidence": 0.85,
                            "reasoning": "마감이 내일이고 중요한 업무입니다.",
                            "parsed_datetime": (
                                datetime.utcnow() + timedelta(days=1)
                            ).isoformat(),
                        }
                    )
                )
            )
        ]
        return mock_response

    mock_client.chat.completions.create = MagicMock(side_effect=default_response)
    return mock_client


# ============================================================================
# User & Auth Fixtures
# ============================================================================


@pytest.fixture
def test_user():
    """Test user object for authentication testing.
    
    Returns a dictionary with user credentials and metadata.
    """
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "password": "test-password-123",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",  # bcrypt hash
        "created_at": datetime.utcnow(),
    }


@pytest.fixture
def auth_token(test_user):
    """Generate a valid JWT token for testing.
    
    Uses the core.security module to create a token.
    Token is valid for 24 hours by default.
    """
    from app.core.security import create_access_token

    token = create_access_token(
        data={
            "sub": test_user["id"],
            "email": test_user["email"],
        }
    )
    return token


# ============================================================================
# FastAPI TestClient Fixture
# ============================================================================


@pytest.fixture
def client():
    """FastAPI TestClient for integration testing.
    
    Uses httpx.Client under the hood.
    Provides synchronous HTTP methods for testing endpoints.
    """
    return TestClient(app)


# ============================================================================
# Korean Task Samples Fixture
# ============================================================================


@pytest.fixture
def korean_task_samples():
    """Korean task samples for AI classification testing.
    
    Returns a list of realistic Korean task descriptions
    covering various urgency/importance combinations.
    """
    return [
        "내일까지 보고서 제출",  # urgent + important
        "다음 주 금요일 팀미팅",  # not urgent + important
        "우유 사기",  # not urgent + not important
        "오늘 자정까지 과제 마감",  # urgent + important
        "언젠가 여행 계획 세우기",  # not urgent + important
    ]


# ============================================================================
# Environment Configuration for Tests
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables.
    
    Automatically runs once per test session.
    Ensures test-specific configuration is loaded.
    """
    import os

    # Load .env.test if it exists
    env_test_path = ".env.test"
    if os.path.exists(env_test_path):
        from dotenv import load_dotenv

        load_dotenv(env_test_path)

    # Ensure test-specific settings
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
