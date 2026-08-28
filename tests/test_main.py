from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_success():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP", "service": "doquest-ai"}


@patch("app.main.memo_analysis_chain")
def test_parse_memo_success(mock_chain):
    mock_chain.ainvoke = AsyncMock(return_value={
        "is_schedule": True,
        "title": "알고리즘 문제 풀이",
        "scheduled_at": "2026-08-18",
        "location": None,
        "summary_info": "백준 골드 DP 문제 풀이 연습",
        "action_links": []
    })

    payload = {
        "memo_id": 100,
        "member_id": 1,
        "content": "내일 저녁 백준 DP 문제 풀기"
    }

    response = client.post("/api/v1/ai/parse-memo", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["is_schedule"] is True
    assert data["title"] == "알고리즘 문제 풀이"
    assert data["scheduled_at"] == "2026-08-18"
    assert data["location"] is None
    assert data["summary_info"] == "백준 골드 DP 문제 풀이 연습"
    assert data["action_links"] == []
    mock_chain.ainvoke.assert_awaited_once_with({"memo_content": payload["content"]})


def test_parse_memo_validation_failure():
    invalid_payload = {"member_id": 1}

    response = client.post("/api/v1/ai/parse-memo", json=invalid_payload)

    assert response.status_code == 422
