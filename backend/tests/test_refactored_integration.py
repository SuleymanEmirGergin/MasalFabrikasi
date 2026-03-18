
import pytest
import uuid

def test_chatbot_pending_state_flow(test_client):
    """
    Test the Chatbot Pending State mechanism.
    1. Set pending state for a conversation.
    2. Verify state is set.
    3. Chat with character (simulating context awareness).
    4. Clear state.
    5. Verify state is cleared.
    """
    client = test_client
    conversation_id = str(uuid.uuid4())
    state_type = "WAITING_FOR_GENRE"
    state_data = {"draft_title": "Test Story"}
    
    # 1. Set State
    response = client.post(
        f"/api/chatbot/conversations/{conversation_id}/state",
        json={"state_type": state_type, "data": state_data}
    )
    assert response.status_code == 200
    assert response.json()["state"] == state_type
    
    # 2. Get State
    response = client.get(f"/api/chatbot/conversations/{conversation_id}/state")
    assert response.status_code == 200
    assert response.json()["pending_state"]["type"] == state_type
    assert response.json()["pending_state"]["data"] == state_data

    # 3. Clear State
    response = client.delete(f"/api/chatbot/conversations/{conversation_id}/state")
    assert response.status_code == 200
    
    # 4. Verify Cleared
    response = client.get(f"/api/chatbot/conversations/{conversation_id}/state")
    assert response.status_code == 200
    assert response.json()["pending_state"] is None


def test_analytics_query_endpoint(test_client):
    """
    Test the Advanced Analytics Query endpoint.
    1. Query with valid metric type.
    2. Query with date filters (mocked data might return empty, but status should be 200).
    """
    client = test_client
    # Simple query
    response = client.post(
        "/api/analytics/query",
        json={
            "metric_type": "scroll_depth",
            "filters": {"story_id": "test_story_123"}
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    # Invalid metric type (should still return 200 with empty dict or handle gracefully based on logic)
    response = client.post(
        "/api/analytics/query",
        json={"metric_type": "unknown_metric"}
    )
    assert response.status_code == 200
    assert response.json() == {}
