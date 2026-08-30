import io
from fastapi.testclient import TestClient

def test_investigation_overview_and_graph(client: TestClient, investigator_token):
    # 1. Create Case
    case_res = client.post(
        "/api/cases",
        json={"case_number": "CASE-GRAPH-01", "case_name": "Graph Test Case"},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    case_id = case_res.json()["id"]

    # 2. Upload sample evidence
    csv_content = (
        "timestamp,event_type,device,event_description\n"
        "2026-08-30T10:15:00Z,USER_LOGON,WORKSTATION-01,User logged in\n"
    ).encode("utf-8")
    client.post(
        "/api/evidence/upload",
        data={"case_id": case_id, "device": "WORKSTATION-01"},
        files={"file": ("logon.csv", io.BytesIO(csv_content), "text/csv")},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 3. Rebuild timeline
    client.post(
        "/api/timeline/rebuild",
        json={"case_id": case_id},
        headers={"Authorization": f"Bearer {investigator_token}"}
    )

    # 4. Check Investigation Overview (5 steps)
    ov_res = client.get(
        f"/api/investigation/overview?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert ov_res.status_code == 200
    steps = ov_res.json()["steps"]
    assert len(steps) == 5
    assert steps[0]["title"] == "Collect Evidence"
    assert steps[0]["status"] == "completed"
    assert steps[1]["title"] == "Normalize Artifacts"
    assert steps[1]["status"] == "completed"
    assert steps[2]["title"] == "Build Timeline"
    assert steps[2]["status"] == "completed"

    # 5. Check Knowledge Graph endpoint
    graph_res = client.get(
        f"/api/investigation/relationships?case_id={case_id}",
        headers={"Authorization": f"Bearer {investigator_token}"}
    )
    assert graph_res.status_code == 200
    g_data = graph_res.json()
    assert g_data["total_nodes"] > 0
    assert g_data["total_links"] > 0
    node_types = {n["type"] for n in g_data["nodes"]}
    assert "Case" in node_types
    assert "Evidence" in node_types
    assert "Artifact" in node_types
