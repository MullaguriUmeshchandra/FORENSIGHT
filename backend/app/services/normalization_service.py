from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.artifact import Artifact
from app.models.evidence import Evidence
from app.processors import get_processor_for_file, RawEvidenceRecord
from app.utils.time_utils import parse_forensic_timestamp
from app.utils.logger import logger

class NormalizationService:
    """Service to normalize heterogeneous digital forensics evidence into standardized artifacts."""

    @staticmethod
    def normalize_evidence_file(
        db: Session,
        evidence: Evidence,
        raw_content: bytes
    ) -> Tuple[List[Artifact], List[Dict[str, Any]]]:
        """
        Extracts, normalizes, deduplicates, and persists artifacts from raw evidence file content.
        Preserves normalization warnings/errors without silently dropping records.
        """
        processor = get_processor_for_file(evidence.filename, raw_content)
        raw_records: List[RawEvidenceRecord] = processor.parse(
            content=raw_content,
            filename=evidence.filename,
            default_device=evidence.device or "Unknown Device"
        )

        artifacts: List[Artifact] = []
        errors: List[Dict[str, Any]] = []
        seen_keys = set()

        for idx, rec in enumerate(raw_records):
            # Parse timestamp into standardized UTC
            parsed_dt = parse_forensic_timestamp(rec.timestamp_raw)
            has_valid_timestamp = parsed_dt is not None

            # Forensic Rule: If timestamp is invalid or missing, do NOT discard record
            if not has_valid_timestamp:
                err_info = {
                    "record_index": idx + 1,
                    "raw_timestamp": str(rec.timestamp_raw),
                    "event_type": rec.event_type,
                    "reason": "Invalid or missing timestamp"
                }
                errors.append(err_info)
                # Assign fallback timestamp as evidence upload/collected time with flagged metadata
                dt_to_store = evidence.collected_at or evidence.uploaded_at or datetime.now(timezone.utc)
                rec_meta = dict(rec.metadata)
                rec_meta["_forensic_normalization_warning"] = "Missing or unparseable raw timestamp"
                rec_meta["_raw_timestamp"] = str(rec.timestamp_raw)
                confidence = 0.5
            else:
                dt_to_store = parsed_dt
                rec_meta = dict(rec.metadata)
                confidence = rec.confidence

            # Deduplication key: (timestamp, device, event_type, description, record_id)
            dedup_key = (
                dt_to_store.isoformat(),
                rec.device.strip().lower(),
                rec.event_type.strip().lower(),
                rec.event_description.strip()[:100].lower(),
                str(rec.source_record_id)
            )

            if dedup_key in seen_keys:
                # Mark as duplicate in metadata
                rec_meta["_is_duplicate"] = True
                rec_meta["_duplicate_of_record_id"] = str(rec.source_record_id)
            else:
                seen_keys.add(dedup_key)

            artifact = Artifact(
                evidence_id=evidence.id,
                case_id=evidence.case_id,
                timestamp=dt_to_store,
                device=rec.device or evidence.device or "Unknown Device",
                event_type=rec.event_type,
                event_description=rec.event_description,
                source=evidence.filename,
                source_record_id=str(rec.source_record_id) if rec.source_record_id else f"rec_{idx+1}",
                metadata_json=rec_meta,
                confidence=confidence
            )
            artifacts.append(artifact)

        if artifacts:
            db.add_all(artifacts)
            db.commit()
            for art in artifacts:
                db.refresh(art)

        logger.info(f"Normalized {len(artifacts)} artifacts from evidence '{evidence.filename}' (errors/warnings: {len(errors)})")
        return artifacts, errors
