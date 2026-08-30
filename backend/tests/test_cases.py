from fastapi.testclient import TestClient

def test_case_lifecycle(client: TestClient, investigator_token, admin_token):
    # 1. Create case
    case_payload = {
        "case_number": "CASE-TEST-001",
        "case_name": "Test Incident Alpha",
        "description": "Investigation into unauthorized USB exfiltration",
        "status": "OPEN"
    }
    create_res = client.post(
        "/api/cases",
        json=case_payload,
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert create_res.status_code == 201
    case_data = create_res.json()
    case_id = case_data["id"]
    assert case_data["case_number"] == "CASE-TEST-001"

    # 2. Get case
    get_res = client.get(
        f"/api/cases/{case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert get_res.status_code == 200
    assert get_res.json()["case_name"] == "Test Incident Alpha"

    # 3. Update case
    update_res = client.put(
        f"/api/cases/{case_id}",
        json={"status": "IN_PROGRESS", "description": "Updated description"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "IN_PROGRESS"

    # 4. List cases
    list_res = client.get(
        "/api/cases",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 5. Delete case (Admin)
    del_res = client.delete(
        f"/api/cases/{case_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert del_res.status_code == 204
