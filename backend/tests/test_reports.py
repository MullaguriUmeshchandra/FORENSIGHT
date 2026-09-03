from fastapi.testclient import TestClient

def test_report_generation_and_download(client: TestClient, investigator_token):
    # 1. Create a case
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-REP-01", "case_name": "Report Test Case"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert case_res.status_code == 201
    case_id = case_res.json()["id"]

    # 2. Generate a report
    gen_res = client.post(
        "/api/reports",
        json={
            "case_id": case_id,
            "title": "Initial Forensic Assessment",
            "report_format": "MARKDOWN"
        },
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert gen_res.status_code == 201
    report_data = gen_res.json()
    report_id = report_data["id"]
    assert report_data["title"] == "Initial Forensic Assessment"

    # 3. List reports for case
    list_res = client.get(
        f"/api/reports?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert list_res.status_code == 200
    assert list_res.json()["total_reports"] >= 1

    # 4. Download report with Authorization Bearer header
    download_header_res = client.get(
        f"/api/reports/{report_id}/download",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert download_header_res.status_code == 200
    assert len(download_header_res.content) > 0

    # 5. Download report with query token (browser direct download)
    download_query_res = client.get(
        f"/api/reports/{report_id}/download?token={investigator_token}"
    )
    assert download_query_res.status_code == 200
    assert len(download_query_res.content) > 0
