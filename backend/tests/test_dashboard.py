import io
from fastapi.testclient import TestClient

def test_dashboard_summary_and_activity(client: TestClient, investigator_token):
    # 1. Create Case
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-DASH-01", "case_name": "Dashboard Test Case"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    case_id = case_res.json()["id"]

    # 2. Ingest Evidence
    csv_content = (
        "timestamp,event_type,device,event_description\n"
        "2026-08-30T10:15:00Z,USER_LOGON,WORKSTATION-01,Logon\n"
        "2026-08-30T10:28:00Z,USB_ATTACH,WORKSTATION-01,USB\n"
        "2026-08-30T10:41:00Z,FILE_ACCESS,WORKSTATION-01,File Access\n"
    ).encode("utf-8")
    client.post(
        "/api/evidence/upload",
        data={"case_id": case_id, "device": "WORKSTATION-01"},
        files={"file": ("sample_system_logs.csv", io.BytesIO(csv_content), "text/csv")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 3. Rebuild timeline
    client.post(
        "/api/timeline/rebuild",
        json={"case_id": case_id},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 4. Fetch dashboard summary
    dash_res = client.get(
        f"/api/dashboard/summary?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert dash_res.status_code == 200
    d = dash_res.json()
    assert d["evidence_sources"] >= 1
    assert d["artifacts_processed"] >= 3
    assert "Unexplained Time Gaps" in d["gap_summary"]
    assert "System Logs" in d["source_breakdown"]

    # 5. Fetch dashboard activity
    act_res = client.get(
        f"/api/dashboard/activity?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert act_res.status_code == 200
    acts = act_res.json()
    assert acts["total"] >= 1
    assert any(a["action"] == "EVIDENCE_UPLOADED" for a in acts["activities"])
