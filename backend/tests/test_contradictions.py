import io
from fastapi.testclient import TestClient

def test_contradiction_detection(client: TestClient, investigator_token):
    # 1. Create Case
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-CONTRA-01", "case_name": "Contradiction Test Case"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    case_id = case_res.json()["id"]

    # 2. Upload Evidence 1: Activity on WORKSTATION-01 at 10:15:00
    csv_1 = (
        "timestamp,event_type,device,event_description\n"
        "2026-08-30T10:15:00Z,INTERACTIVE_LOGON,WORKSTATION-01,User active on console\n"
    ).encode("utf-8")
    client.post(
        "/api/evidence/upload",
        data={"case_id": case_id, "device": "WORKSTATION-01"},
        files={"file": ("source1.csv", io.BytesIO(csv_1), "text/csv")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 3. Upload Evidence 2: Simultaneous Activity on REMOTE-LAPTOP-02 at 10:15:05
    csv_2 = (
        "timestamp,event_type,device,event_description\n"
        "2026-08-30T10:15:05Z,VPN_AUTHENTICATION,REMOTE-LAPTOP-02,VPN session established from Berlin\n"
    ).encode("utf-8")
    client.post(
        "/api/evidence/upload",
        data={"case_id": case_id, "device": "REMOTE-LAPTOP-02"},
        files={"file": ("source2.csv", io.BytesIO(csv_2), "text/csv")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 4. Detect contradictions
    contra_res = client.post(
        f"/api/contradictions/detect?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert contra_res.status_code == 200
    data = contra_res.json()
    assert data["total_contradictions"] >= 1
    assert any("WORKSTATION-01" in c["description"] and "REMOTE-LAPTOP-02" in c["description"] for c in data["contradictions"])
