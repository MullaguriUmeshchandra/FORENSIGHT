import io
from fastapi.testclient import TestClient

def test_timeline_reconstruction(client: TestClient, investigator_token):
    # 1. Create case
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-TL-01", "case_name": "Timeline Reconstruction Test"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    case_id = case_res.json()["id"]

    # 2. Upload out-of-order logs to verify chronological sorting
    csv_1 = (
        "timestamp,event_type,device,event_description\n"
        "2026-08-30T10:41:00Z,FILE_ACCESS,WORKSTATION-01,File FIN_2026.xlsx accessed\n"
        "2026-08-30T10:15:00Z,USER_LOGON,WORKSTATION-01,User logged in\n"
        "2026-08-30T10:28:00Z,USB_ATTACH,WORKSTATION-01,USB attached\n"
    ).encode("utf-8")

    client.post(
        "/api/evidence/upload",
        data={"case_id": case_id, "device": "WORKSTATION-01"},
        files={"file": ("logs.csv", io.BytesIO(csv_1), "text/csv")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 3. Rebuild timeline
    rebuild_res = client.post(
        "/api/timeline/rebuild",
        json={"case_id": case_id},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert rebuild_res.status_code == 200
    assert rebuild_res.json()["events_reconstructed"] == 3

    # 4. Fetch timeline and verify sorted order
    timeline_res = client.get(
        f"/api/timeline?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert timeline_res.status_code == 200
    events = timeline_res.json()["events"]
    assert len(events) == 3
    assert "User logged in" in events[0]["event"]
    assert "USB attached" in events[1]["event"]
    assert "File FIN_2026.xlsx" in events[2]["event"]
