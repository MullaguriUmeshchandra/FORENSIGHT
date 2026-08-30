import io
from fastapi.testclient import TestClient
from app.utils.hasher import compute_sha256_bytes

def test_evidence_upload_and_hashing(client: TestClient, investigator_token):
    # 1. Create a case first
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-EV-01", "case_name": "Evidence Test Case"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert case_res.status_code == 201
    case_id = case_res.json()["id"]

    # 2. Upload sample CSV evidence
    csv_content = b"timestamp,event_type,device,event_description\n2026-08-30T10:15:00Z,LOGON,PC-1,User logon\n"
    expected_hash = compute_sha256_bytes(csv_content)

    upload_res = client.post(
        "/api/evidence/upload",
        data={"case_id": case_id, "device": "PC-1"},
        files={"file": ("test_log.csv", io.BytesIO(csv_content), "text/csv")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    assert upload_data["artifacts_created"] == 1
    assert upload_data["evidence"]["file_hash"] == expected_hash
    assert upload_data["evidence"]["filename"] == "test_log.csv"

    # 3. Retrieve evidence list
    list_res = client.get(
        f"/api/evidence?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1

def test_reject_unsupported_file(client: TestClient, investigator_token):
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-EV-02", "case_name": "Invalid File Test"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    case_id = case_res.json()["id"]

    bad_content = b"MZ\x90\x00\x03\x00\x00\x00"
    upload_res = client.post(
        "/api/evidence/upload",
        data={"case_id": case_id},
        files={"file": ("malicious.exe", io.BytesIO(bad_content), "application/x-msdownload")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert upload_res.status_code == 400
    assert "Unsupported file type" in upload_res.json()["detail"]
