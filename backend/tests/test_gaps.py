import io
from fastapi.testclient import TestClient
from app.ml.gap_analyzer import evaluate_gap_severity, format_duration
from app.models.gap import GapSeverity

def test_gap_threshold_evaluations():
    # Less than 2 minutes (100s) -> ignored
    sev, is_sig = evaluate_gap_severity(100)
    assert not is_sig

    # 2-5 minutes (180s = 3m) -> Low
    sev, is_sig = evaluate_gap_severity(180)
    assert is_sig and sev == GapSeverity.LOW

    # 5-15 minutes (780s = 13m) -> Medium
    sev, is_sig = evaluate_gap_severity(780)
    assert is_sig and sev == GapSeverity.MEDIUM

    # > 15 minutes (1200s = 20m) -> High
    sev, is_sig = evaluate_gap_severity(1200)
    assert is_sig and sev == GapSeverity.HIGH

def test_sample_case_gap_detection(client: TestClient, investigator_token):
    # 1. Create CASE-001
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-001-GAP-TEST", "case_name": "Sample Gap Test Case"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    case_id = case_res.json()["id"]

    # 2. Ingest 10:28 USB Connected and 10:41 File Access
    csv_content = (
        "timestamp,event_type,device,event_description\n"
        "2026-08-30T10:15:00Z,USER_LOGON,WORKSTATION-01,User logged in\n"
        "2026-08-30T10:21:00Z,BROWSER_START,WORKSTATION-01,Browser launched\n"
        "2026-08-30T10:28:00Z,USB_ATTACH,WORKSTATION-01,USB Storage attached\n"
        "2026-08-30T10:41:00Z,FILE_ACCESS,WORKSTATION-01,Confidential File Copied\n"
        "2026-08-30T10:46:00Z,NETWORK_ACTIVITY,WORKSTATION-01,Outbound Transfer\n"
    ).encode("utf-8")

    client.post(
        "/api/evidence/upload",
        data={"case_id": case_id, "device": "WORKSTATION-01"},
        files={"file": ("sample_evidence.csv", io.BytesIO(csv_content), "text/csv")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 3. Rebuild timeline (which triggers gap detection)
    client.post(
        "/api/timeline/rebuild",
        json={"case_id": case_id},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 4. Fetch gaps
    gaps_res = client.get(
        f"/api/gaps?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert gaps_res.status_code == 200
    gap_data = gaps_res.json()
    assert gap_data["total_gaps"] >= 1

    # Find the 13-minute gap between 10:28 and 10:41
    gap_13m = next((g for g in gap_data["gaps"] if g["duration_seconds"] == 780), None)
    assert gap_13m is not None
    assert gap_13m["severity"] == "MEDIUM"
    assert "unexplained transition" in gap_13m["reason"].lower()
    assert "10:28:00" in gap_13m["reason"]
    assert "10:41:00" in gap_13m["reason"]
