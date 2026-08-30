import io
from fastapi.testclient import TestClient

def test_recommendations_generation(client: TestClient, investigator_token):
    # 1. Create Case
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-REC-01", "case_name": "Recommendations Test Case"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    case_id = case_res.json()["id"]

    # 2. Upload events with a gap
    csv_content = (
        "timestamp,event_type,device,event_description\n"
        "2026-08-30T10:28:00Z,USB_ATTACH,WORKSTATION-01,USB Storage attached\n"
        "2026-08-30T10:41:00Z,FILE_ACCESS,WORKSTATION-01,Confidential File Copied\n"
    ).encode("utf-8")

    client.post(
        "/api/evidence/upload",
        data={"case_id": case_id, "device": "WORKSTATION-01"},
        files={"file": ("events.csv", io.BytesIO(csv_content), "text/csv")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 3. Rebuild timeline (which auto-detects gaps and generates recommendations)
    client.post(
        "/api/timeline/rebuild",
        json={"case_id": case_id},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 4. Fetch recommendations
    rec_res = client.get(
        f"/api/recommendations?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert rec_res.status_code == 200
    recs = rec_res.json()
    assert recs["total_recommendations"] >= 1
    assert any("MFT" in r["title"] or "Journal" in r["title"] or "Prefetch" in r["description"] for r in recs["recommendations"])
