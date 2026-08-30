from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models.artifact import Artifact
from app.models.contradiction import ContradictionType, ContradictionSeverity

class ContradictionDetector:
    """Forensic multi-source contradiction detector across normalized artifacts."""

    @staticmethod
    def detect_contradictions(artifacts: List[Artifact]) -> List[Dict[str, Any]]:
        """
        Compare artifacts from different sources and detect inconsistencies.
        Forensic Rule: Do not automatically decide which evidence is correct.
        """
        contradictions: List[Dict[str, Any]] = []
        if len(artifacts) < 2:
            return contradictions

        # 1. Device and User concurrency conflicts
        # Group by user/action window if user info present in metadata
        for i in range(len(artifacts)):
            for j in range(i + 1, len(artifacts)):
                a1 = artifacts[i]
                a2 = artifacts[j]

                # If from same evidence source, skip cross-source comparison
                if a1.evidence_id == a2.evidence_id:
                    continue

                t1: datetime = a1.timestamp
                t2: datetime = a2.timestamp
                time_diff = abs((t1 - t2).total_seconds())

                # Check 1: Incompatible simultaneous activity on different physical devices
                # (e.g. within 30 seconds on different hosts)
                if time_diff <= 30 and a1.device != a2.device and a1.device != "Unknown Device" and a2.device != "Unknown Device":
                    desc = (
                        f"Concurrent conflicting activity recorded across separate devices '{a1.device}' "
                        f"and '{a2.device}' within {int(time_diff)} seconds: "
                        f"Source '{a1.source}' reported '{a1.event_type}' at {t1.strftime('%H:%M:%S')} UTC, "
                        f"while source '{a2.source}' reported '{a2.event_type}' at {t2.strftime('%H:%M:%S')} UTC."
                    )
                    contradictions.append({
                        "artifact_a_id": a1.id,
                        "artifact_b_id": a2.id,
                        "contradiction_type": ContradictionType.DEVICE_CONFLICT,
                        "description": desc,
                        "severity": ContradictionSeverity.HIGH if time_diff < 5 else ContradictionSeverity.MEDIUM,
                        "confidence": 0.95
                    })

                # Check 2: Timestamp conflict for identical event identifier/file
                rec_id1 = a1.source_record_id
                rec_id2 = a2.source_record_id
                meta1 = a1.metadata_json or {}
                meta2 = a2.metadata_json or {}
                
                # Check if referring to same filename or action with divergent timestamps (> 60s)
                fn1 = meta1.get("file_name") or meta1.get("filename") or meta1.get("path")
                fn2 = meta2.get("file_name") or meta2.get("filename") or meta2.get("path")

                if fn1 and fn2 and str(fn1).strip().lower() == str(fn2).strip().lower() and time_diff > 60:
                    desc = (
                        f"Conflicting timestamps for file '{fn1}': "
                        f"Source '{a1.source}' logged access at {t1.strftime('%H:%M:%S')} UTC, "
                        f"whereas source '{a2.source}' recorded activity at {t2.strftime('%H:%M:%S')} UTC "
                        f"(divergence: {int(time_diff)} seconds)."
                    )
                    contradictions.append({
                        "artifact_a_id": a1.id,
                        "artifact_b_id": a2.id,
                        "contradiction_type": ContradictionType.TIMESTAMP_CONFLICT,
                        "description": desc,
                        "severity": ContradictionSeverity.MEDIUM,
                        "confidence": 0.85
                    })

                # Check 3: Impossible sequence (e.g., USB Disconnect before USB File Copy)
                desc1_lower = a1.event_description.lower()
                desc2_lower = a2.event_description.lower()
                if "usb disconnect" in desc1_lower and "usb" in desc2_lower and "access" in desc2_lower:
                    if t1 < t2:
                        desc = (
                            f"Impossible chronological sequence: USB disconnection was logged by '{a1.source}' "
                            f"at {t1.strftime('%H:%M:%S')} UTC prior to USB file access logged by '{a2.source}' "
                            f"at {t2.strftime('%H:%M:%S')} UTC."
                        )
                        contradictions.append({
                            "artifact_a_id": a1.id,
                            "artifact_b_id": a2.id,
                            "contradiction_type": ContradictionType.EVENT_ORDER_CONFLICT,
                            "description": desc,
                            "severity": ContradictionSeverity.HIGH,
                            "confidence": 0.95
                        })

        return contradictions
