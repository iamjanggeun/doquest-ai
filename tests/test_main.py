from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_success():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP", "service": "doquest-ai"}

@patch("app.main.invoke_memo_chain", new_callable=AsyncMock)
def test_parse_memo_success(mock_chain):
    # Given: Mock 데이터 설정
    mock_chain.return_value = {
        "is_schedule": True,
        "title": "알고리즘 문제 풀이",
        "target_date": "2026-08-18",
        "summary_info": "백준 골드 DP 문제 풀이 연습",
        "action_links": ["https://www.acmicpc.net"]
    }

    payload = {
        "member_id": 1,
        "content": "내일 저녁 백준 DP 문제 풀기"
    }

    # When
    response = client.post("/api/v1/ai/parse-memo", json=payload)

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["is_schedule"] is True
    assert data["title"] == "알고리즘 문제 풀이"
    assert data["target_date"] == "2026-08-18"
    assert len(data["action_links"]) == 1

def test_parse_memo_validation_failure():
    invalid_payload = {"member_id": 1}
    response = client.post("/api/v1/ai/parse-memo", json=invalid_payload)
    assert response.status_code == 422