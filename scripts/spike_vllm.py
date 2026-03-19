#!/usr/bin/env python3
"""
vLLM Spike Test: Validate AI endpoint with Korean task samples
Tests: endpoint accessibility, model identification, Korean parsing capability
"""

import json
import os
import time
import sys
from datetime import datetime
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Install with: pip install openai")
    sys.exit(1)

# Configuration
VLLM_BASE_URL = "https://air.changwon.ac.kr/simon/v1"
API_KEY = os.getenv("AI_API_KEY", "")

# Korean task samples for testing
KOREAN_TASKS = [
    "내일 3시까지 보고서 제출",  # Tomorrow 3pm report submission
    "다음 주 금요일 팀미팅",      # Next Friday team meeting
    "우유 사기",                   # Buy milk (no date)
    "오늘 자정까지 과제 마감",    # Today midnight assignment deadline
    "언젠가 여행 계획 세우기",    # Someday plan a trip
]

CATEGORIZATION_PROMPT = """당신은 할일 분류 전문가입니다. 다음 할일을 긴급도(urgency: 1-5)와 중요도(importance: 1-5)로 분류하세요.
응답은 JSON 형식으로 해주세요: {{"urgency": <1-5>, "importance": <1-5>, "parsed_date": "<날짜 또는 null>"}}

할일: {task}"""


def test_endpoint_accessibility() -> dict:
    """Test if vLLM endpoint is accessible"""
    print("\n[1/3] Testing endpoint accessibility...")
    result = {
        "accessible": False,
        "status_code": None,
        "error": None,
        "model_name": None,
    }

    try:
        client = OpenAI(base_url=VLLM_BASE_URL, api_key=API_KEY)
        # Try to list models
        models = client.models.list()
        result["accessible"] = True
        result["status_code"] = 200

        # Extract model name
        if hasattr(models, "data") and len(models.data) > 0:
            result["model_name"] = models.data[0].id
            print(f"✓ Endpoint accessible. Model: {result['model_name']}")
        else:
            print("✓ Endpoint accessible but no models returned")

    except Exception as e:
        result["error"] = str(e)
        print(f"✗ Endpoint test failed: {e}")

    return result


def test_korean_tasks(client: Optional[OpenAI], model_name: Optional[str]) -> dict:
    """Test Korean task parsing with 5 samples"""
    print("\n[2/3] Testing Korean task parsing...")
    results = {
        "total_tasks": len(KOREAN_TASKS),
        "successful": 0,
        "failed": 0,
        "tasks": [],
        "average_response_time": 0,
    }

    if not client or not model_name:
        print("✗ Cannot test tasks: client or model not available")
        results["error"] = "Client initialization failed"
        return results

    response_times = []

    for i, task in enumerate(KOREAN_TASKS, 1):
        print(f"  Task {i}/5: {task[:30]}...")
        task_result = {
            "task": task,
            "success": False,
            "response_time": 0,
            "response": None,
            "error": None,
        }

        try:
            start_time = time.time()

            message = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": CATEGORIZATION_PROMPT.format(task=task)}],
                temperature=0.3,
                max_tokens=100,
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": False},
                    "top_k": 20,
                },
            )

            response_time = time.time() - start_time
            response_times.append(response_time)
            task_result["response_time"] = response_time

            # Extract response text
            response_text = (message.choices[0].message.content or "").strip()
            task_result["response"] = response_text

            # Try to parse as JSON
            try:
                parsed = json.loads(response_text)
                task_result["success"] = True
                results["successful"] += 1
                print(f"    ✓ Success ({response_time:.2f}s): {parsed}")
            except json.JSONDecodeError:
                # Response is not valid JSON, but request succeeded
                task_result["success"] = False
                task_result["error"] = "Response not valid JSON"
                results["failed"] += 1
                print(f"    ⚠ Invalid JSON ({response_time:.2f}s): {response_text[:50]}")

        except Exception as e:
            task_result["error"] = str(e)
            results["failed"] += 1
            print(f"    ✗ Error: {e}")

        results["tasks"].append(task_result)

    if response_times:
        results["average_response_time"] = sum(response_times) / len(response_times)

    print(f"\n  Summary: {results['successful']}/{results['total_tasks']} successful")
    if results["average_response_time"]:
        print(f"  Average response time: {results['average_response_time']:.2f}s")

    return results


def main():
    """Main spike test execution"""
    print("=" * 60)
    print("vLLM Spike Test: Korean Task Parsing")
    print("=" * 60)
    print(f"Endpoint: {VLLM_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Test 1: Endpoint accessibility
    endpoint_result = test_endpoint_accessibility()

    # Test 2: Korean task parsing (only if endpoint is accessible)
    client = None
    if endpoint_result["accessible"]:
        try:
            client = OpenAI(base_url=VLLM_BASE_URL, api_key=API_KEY)
        except Exception as e:
            print(f"Failed to create client: {e}")

    korean_result = test_korean_tasks(client, endpoint_result.get("model_name"))

    # Compile final results
    final_results = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": VLLM_BASE_URL,
        "endpoint_test": endpoint_result,
        "korean_tasks_test": korean_result,
        "summary": {
            "endpoint_accessible": endpoint_result["accessible"],
            "model_identified": endpoint_result.get("model_name") is not None,
            "model_name": endpoint_result.get("model_name"),
            "korean_success_rate": f"{korean_result['successful']}/{korean_result['total_tasks']}",
            "average_response_time": korean_result.get("average_response_time", 0),
        },
    }

    # Print summary
    print("\n" + "=" * 60)
    print("SPIKE TEST SUMMARY")
    print("=" * 60)
    print(json.dumps(final_results["summary"], indent=2, ensure_ascii=False))

    # Save results to file
    output_file = ".sisyphus/evidence/task-6-vllm-spike.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Results saved to {output_file}")

    return final_results


if __name__ == "__main__":
    main()
