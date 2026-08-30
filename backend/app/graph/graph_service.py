from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.graph.neo4j_client import neo4j_client
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.artifact import Artifact
from app.models.timeline import TimelineEvent
from app.schemas.investigation import GraphNode, GraphLink, GraphDataResponse
from app.utils.logger import logger

class GraphService:
    """Service to create and query knowledge graph relationships in Neo4j."""

    @staticmethod
    def sync_evidence_to_graph(evidence: Evidence, artifacts: List[Artifact]) -> None:
        """Sync evidence and its artifacts to Neo4j."""
        if not neo4j_client.is_available:
            return

        query = """
        MERGE (c:Case {id: $case_id})
        MERGE (e:Evidence {id: $evidence_id})
        SET e.filename = $filename, e.source_type = $source_type, e.hash = $file_hash
        MERGE (c)-[:CASE_HAS_EVIDENCE]->(e)
        MERGE (s:Source {name: $source_type})
        MERGE (e)-[:SOURCED_FROM]->(s)
        """
        neo4j_client.run_query(query, {
            "case_id": evidence.case_id,
            "evidence_id": evidence.id,
            "filename": evidence.filename,
            "source_type": str(evidence.source_type.value if hasattr(evidence.source_type, 'value') else evidence.source_type),
            "file_hash": evidence.file_hash,
        })

        # Batch insert artifacts
        for art in artifacts:
            art_query = """
            MATCH (e:Evidence {id: $evidence_id})
            MERGE (a:Artifact {id: $artifact_id})
            SET a.event_type = $event_type, a.timestamp = $timestamp, a.description = $description
            MERGE (e)-[:EVIDENCE_CONTAINS_ARTIFACT]->(a)
            MERGE (d:Device {name: $device})
            MERGE (a)-[:ARTIFACT_FROM_DEVICE]->(d)
            """
            neo4j_client.run_query(art_query, {
                "evidence_id": evidence.id,
                "artifact_id": art.id,
                "event_type": art.event_type,
                "timestamp": art.timestamp.isoformat(),
                "description": art.event_description,
                "device": art.device or "Unknown Device"
            })

    @staticmethod
    def sync_timeline_to_graph(events: List[TimelineEvent]) -> None:
        """Sync reconstructed timeline events and their chronological sequence to Neo4j."""
        if not neo4j_client.is_available or not events:
            return

        sorted_events = sorted(events, key=lambda x: x.timestamp)
        for i, ev in enumerate(sorted_events):
            ev_query = """
            MERGE (c:Case {id: $case_id})
            MERGE (ev:Event {id: $event_id})
            SET ev.event = $event_text, ev.timestamp = $timestamp, ev.status = $status, ev.device = $device
            MERGE (c)-[:CASE_HAS_EVENT]->(ev)
            """
            neo4j_client.run_query(ev_query, {
                "case_id": ev.case_id,
                "event_id": ev.id,
                "event_text": ev.event,
                "timestamp": ev.timestamp.isoformat(),
                "status": str(ev.status.value if hasattr(ev.status, 'value') else ev.status),
                "device": ev.device
            })

            # Precedence relationship
            if i > 0:
                prev_ev = sorted_events[i - 1]
                prec_query = """
                MATCH (e1:Event {id: $prev_id}), (e2:Event {id: $curr_id})
                MERGE (e1)-[:EVENT_PRECEDES_EVENT]->(e2)
                """
                neo4j_client.run_query(prec_query, {
                    "prev_id": prev_ev.id,
                    "curr_id": ev.id
                })

            # Supporting evidence relationship
            if ev.evidence_id:
                supp_query = """
                MATCH (e:Evidence {id: $evidence_id}), (ev:Event {id: $event_id})
                MERGE (e)-[:EVIDENCE_SUPPORTS_EVENT]->(ev)
                """
                neo4j_client.run_query(supp_query, {
                    "evidence_id": ev.evidence_id,
                    "event_id": ev.id
                })

            # Artifact generates event
            if ev.related_artifacts:
                for art_id in ev.related_artifacts:
                    if isinstance(art_id, int):
                        gen_query = """
                        MATCH (a:Artifact {id: $art_id}), (ev:Event {id: $event_id})
                        MERGE (a)-[:ARTIFACT_GENERATES_EVENT]->(ev)
                        """
                        neo4j_client.run_query(gen_query, {
                            "art_id": art_id,
                            "event_id": ev.id
                        })

    @staticmethod
    def get_case_graph(db: Session, case_id: int) -> GraphDataResponse:
        """
        Retrieve complete node-link graph for a case.
        Queries Neo4j if available, or constructs exact graph from relational models.
        """
        nodes_dict: Dict[str, GraphNode] = {}
        links: List[GraphLink] = []

        # 1. Fetch case
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return GraphDataResponse(case_id=case_id, nodes=[], links=[], total_nodes=0, total_links=0)

        case_node_id = f"case_{case.id}"
        nodes_dict[case_node_id] = GraphNode(
            id=case_node_id,
            label=f"Case: {case.case_number}",
            type="Case",
            properties={"case_number": case.case_number, "name": case.case_name, "status": str(case.status)}
        )

        # 2. Evidence
        evidence_items = db.query(Evidence).filter(Evidence.case_id == case_id).all()
        for ev in evidence_items:
            ev_node_id = f"evidence_{ev.id}"
            nodes_dict[ev_node_id] = GraphNode(
                id=ev_node_id,
                label=f"Evidence: {ev.filename}",
                type="Evidence",
                properties={"filename": ev.filename, "source_type": str(ev.source_type), "hash": ev.file_hash}
            )
            links.append(GraphLink(
                source=case_node_id,
                target=ev_node_id,
                type="CASE_HAS_EVIDENCE"
            ))

            # Source Node
            src_node_id = f"source_{str(ev.source_type)}"
            if src_node_id not in nodes_dict:
                nodes_dict[src_node_id] = GraphNode(
                    id=src_node_id,
                    label=f"Source: {str(ev.source_type)}",
                    type="Source",
                    properties={"source_type": str(ev.source_type)}
                )
            links.append(GraphLink(
                source=ev_node_id,
                target=src_node_id,
                type="SOURCED_FROM"
            ))

        # 3. Artifacts
        artifacts = db.query(Artifact).filter(Artifact.case_id == case_id).all()
        for art in artifacts:
            art_node_id = f"artifact_{art.id}"
            nodes_dict[art_node_id] = GraphNode(
                id=art_node_id,
                label=f"Artifact: {art.event_type}",
                type="Artifact",
                properties={"event_type": art.event_type, "timestamp": art.timestamp.isoformat(), "desc": art.event_description[:60]}
            )
            ev_node_id = f"evidence_{art.evidence_id}"
            if ev_node_id in nodes_dict:
                links.append(GraphLink(
                    source=ev_node_id,
                    target=art_node_id,
                    type="EVIDENCE_CONTAINS_ARTIFACT"
                ))

            # Device Node
            if art.device:
                dev_node_id = f"device_{art.device.replace(' ', '_')}"
                if dev_node_id not in nodes_dict:
                    nodes_dict[dev_node_id] = GraphNode(
                        id=dev_node_id,
                        label=f"Device: {art.device}",
                        type="Device",
                        properties={"device_name": art.device}
                    )
                links.append(GraphLink(
                    source=art_node_id,
                    target=dev_node_id,
                    type="ARTIFACT_FROM_DEVICE"
                ))

        # 4. Timeline Events
        events = db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).order_by(TimelineEvent.timestamp.asc()).all()
        for i, ev in enumerate(events):
            ev_node_id = f"event_{ev.id}"
            nodes_dict[ev_node_id] = GraphNode(
                id=ev_node_id,
                label=f"Event: {ev.event[:40]}",
                type="Event",
                properties={"event": ev.event, "timestamp": ev.timestamp.isoformat(), "status": str(ev.status)}
            )

            # Precedence link
            if i > 0:
                prev_ev_id = f"event_{events[i - 1].id}"
                links.append(GraphLink(
                    source=prev_ev_id,
                    target=ev_node_id,
                    type="EVENT_PRECEDES_EVENT"
                ))

            # Evidence support
            if ev.evidence_id:
                sup_ev_id = f"evidence_{ev.evidence_id}"
                if sup_ev_id in nodes_dict:
                    links.append(GraphLink(
                        source=sup_ev_id,
                        target=ev_node_id,
                        type="EVIDENCE_SUPPORTS_EVENT"
                    ))

            # Artifact link
            if ev.related_artifacts:
                for art_id in ev.related_artifacts:
                    art_node_id = f"artifact_{art_id}"
                    if art_node_id in nodes_dict:
                        links.append(GraphLink(
                            source=art_node_id,
                            target=ev_node_id,
                            type="ARTIFACT_GENERATES_EVENT"
                        ))

        nodes_list = list(nodes_dict.values())
        return GraphDataResponse(
            case_id=case_id,
            nodes=nodes_list,
            links=links,
            total_nodes=len(nodes_list),
            total_links=len(links)
        )
