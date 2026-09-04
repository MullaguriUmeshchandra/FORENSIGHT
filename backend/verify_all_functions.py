import os
import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_full_pipeline():
    client = httpx.Client(base_url=BASE_URL, timeout=15.0)
    
    print("=== 1. Health Check ===")
    r = client.get("/health")
    assert r.status_code == 200, f"Health failed: {r.status_code}"
    print("Health:", r.json())

    print("\n=== 2. Auth Login ===")
    r = client.post("/api/auth/login", json={"username": "investigator", "password": "Investigator123!"})
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully as investigator. Token obtained.")

    print("\n=== 3. Cases API ===")
    r = client.get("/api/cases", headers=headers)
    assert r.status_code == 200
    cases = r.json()["cases"]
    print(f"Cases count: {len(cases)}")
    for c in cases:
        print(f"  - [{c['case_number']}] {c['case_name']} (ID: {c['id']})")
    case_id = cases[0]["id"]

    print(f"\n=== 4. Evidence Inventory for Case {case_id} ===")
    r = client.get(f"/api/evidence?case_id={case_id}", headers=headers)
    assert r.status_code == 200
    evidence = r.json()["evidence"]
    print(f"Evidence items count: {len(evidence)}")
    for e in evidence:
        print(f"  - Evidence #{e['id']}: {e['filename']} [{e['source_type']}] on {e['device']}")

    print(f"\n=== 5. Reconstructed Timeline Events for Case {case_id} ===")
    r = client.get(f"/api/timeline?case_id={case_id}&limit=100", headers=headers)
    assert r.status_code == 200
    events = r.json()["events"]
    print(f"Timeline events count: {len(events)}")
    for ev in events[:5]:
        print(f"  - [{ev['timestamp']}] ({ev['device']}) {ev['event']} [Source: {ev['source']}]")

    print(f"\n=== 6. Forensic Gaps Analysis for Case {case_id} ===")
    r = client.get(f"/api/gaps?case_id={case_id}", headers=headers)
    assert r.status_code == 200
    gap_summary = r.json()
    print(f"Total Gaps: {gap_summary['total_gaps']}")
    for g in gap_summary["gaps"][:4]:
        print(f"  - Gap [{g['severity']}]: {g['start_time']} to {g['end_time']} ({g.get('formatted_duration')}) - {g['reason'][:70]}...")

    print(f"\n=== 7. Cross-Source Contradictions for Case {case_id} ===")
    r = client.get(f"/api/contradictions?case_id={case_id}", headers=headers)
    assert r.status_code == 200
    contradictions = r.json()["contradictions"]
    print(f"Total Contradictions: {len(contradictions)}")
    for contra in contradictions:
        print(f"  - [{contra['contradiction_type']} | Severity: {contra['severity']} | Conf: {contra['confidence']}]")
        print(f"    Description: {contra['description']}")

    print(f"\n=== 8. Investigative Recommendations for Case {case_id} ===")
    r = client.get(f"/api/recommendations?case_id={case_id}", headers=headers)
    assert r.status_code == 200
    recs = r.json()["recommendations"]
    print(f"Total Recommendations: {len(recs)}")
    for rec in recs[:5]:
        print(f"  - [{rec['priority']}] {rec['title']} ({rec['recommendation_type']})")

    print(f"\n=== 9. Knowledge Graph for Case {case_id} ===")
    r = client.get(f"/api/investigation/overview?case_id={case_id}", headers=headers)
    assert r.status_code == 200
    overview = r.json()
    print("Investigation Steps:")
    for s in overview["steps"]:
        print(f"  Step {s['step_number']}: {s['title']} -> {s['status']} (count: {s.get('count')})")
    
    r = client.get(f"/api/investigation/relationships?case_id={case_id}", headers=headers)
    assert r.status_code == 200
    graph = r.json()
    print(f"Graph Data: {len(graph['nodes'])} Nodes, {len(graph['links'])} Links")
    for n in graph["nodes"][:5]:
        print(f"  - Node [{n['type']}]: {n['label']}")

    print(f"\n=== 10. Reports for Case {case_id} ===")
    r = client.get(f"/api/reports?case_id={case_id}", headers=headers)
    assert r.status_code == 200
    reports = r.json()["reports"]
    print(f"Total Reports: {len(reports)}")
    report_id = reports[0]["id"]
    print(f"  - Report #{report_id}: {reports[0]['title']}")

    print("\n=== 11. Report Download Authentication Tests ===")
    # Header auth
    r_hdr = client.get(f"/api/reports/{report_id}/download", headers=headers)
    assert r_hdr.status_code == 200, f"Download with Header failed: {r_hdr.status_code}"
    print(f"Header auth download succeeded: {len(r_hdr.content)} bytes")

    # Query param auth
    r_qry = client.get(f"/api/reports/{report_id}/download?token={token}")
    assert r_qry.status_code == 200, f"Download with Query Token failed: {r_qry.status_code}"
    print(f"Query token auth download succeeded: {len(r_qry.content)} bytes")

    print("\n=== 12. New Evidence Upload & Automatic Rebuild Verification ===")
    sample_file_path = "sample_evidence/05_cloudtrail_activity.json"
    with open(sample_file_path, "rb") as f:
        files = {"file": ("cloudtrail_test_upload.json", f.read(), "application/json")}
        data = {"case_id": case_id, "device": "CLOUD-AWS", "source_type": "CLOUD_ACTIVITY"}
        r_upload = client.post("/api/evidence/upload", headers=headers, files=files, data=data)
    assert r_upload.status_code == 201, f"Upload failed: {r_upload.status_code} {r_upload.text}"
    print("Upload result:", r_upload.json()["message"])

    # Trigger rebuild
    r_reb = client.post("/api/timeline/rebuild", headers=headers, json={"case_id": case_id})
    assert r_reb.status_code == 200
    print("Timeline Rebuilt:", r_reb.json())

    print("\n=======================================================")
    print("ALL 12 FORENSIC FUNCTIONS AND VERIFICATIONS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    test_full_pipeline()
