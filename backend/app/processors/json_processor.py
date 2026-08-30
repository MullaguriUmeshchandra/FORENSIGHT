import json
from typing import List, Dict, Any
from app.processors.base import BaseProcessor, RawEvidenceRecord
from app.processors.csv_processor import TIMESTAMP_HEADERS, EVENT_DESC_HEADERS, EVENT_TYPE_HEADERS, DEVICE_HEADERS, ID_HEADERS

class JSONProcessor(BaseProcessor):
    """Processor for JSON and JSON-Lines (NDJSON) forensic files."""

    def can_process(self, filename: str, content: bytes) -> bool:
        fn = filename.lower()
        return fn.endswith(".json") or fn.endswith(".jsonl") or fn.endswith(".ndjson")

    def _extract_from_dict(self, d: Dict[str, Any], idx: int, filename: str, default_device: str) -> RawEvidenceRecord:
        d_lower = {k.lower().strip().replace(" ", "_"): (k, v) for k, v in d.items()}
        
        # Timestamp
        ts = None
        for cand in TIMESTAMP_HEADERS:
            if cand in d_lower:
                ts = d_lower[cand][1]
                break

        # Event type
        etype = None
        for cand in EVENT_TYPE_HEADERS:
            if cand in d_lower:
                etype = d_lower[cand][1]
                break
        if not etype:
            etype = "JSON_EVENT"

        # Event Description
        desc = None
        for cand in EVENT_DESC_HEADERS:
            if cand in d_lower:
                desc = d_lower[cand][1]
                break
        if not desc:
            desc = json.dumps(d)

        # Device
        device = default_device
        for cand in DEVICE_HEADERS:
            if cand in d_lower and d_lower[cand][1]:
                device = str(d_lower[cand][1])
                break

        # ID
        rec_id = str(idx)
        for cand in ID_HEADERS:
            if cand in d_lower and d_lower[cand][1]:
                rec_id = str(d_lower[cand][1])
                break

        return RawEvidenceRecord(
            timestamp_raw=ts,
            event_type=str(etype),
            event_description=str(desc),
            device=device,
            source=filename,
            source_record_id=rec_id,
            metadata=d,
            confidence=1.0
        )

    def parse(self, content: bytes, filename: str, default_device: str = "Unknown Device") -> List[RawEvidenceRecord]:
        records: List[RawEvidenceRecord] = []
        text = content.decode("utf-8-sig", errors="replace")

        # Try parsing as standard JSON
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                for idx, item in enumerate(parsed):
                    if isinstance(item, dict):
                        records.append(self._extract_from_dict(item, idx + 1, filename, default_device))
                return records
            elif isinstance(parsed, dict):
                # Look for nested array keys
                for key in ["events", "logs", "artifacts", "records", "data", "items"]:
                    if key in parsed and isinstance(parsed[key], list):
                        for idx, item in enumerate(parsed[key]):
                            if isinstance(item, dict):
                                records.append(self._extract_from_dict(item, idx + 1, filename, default_device))
                        return records
                # Single object
                records.append(self._extract_from_dict(parsed, 1, filename, default_device))
                return records
        except json.JSONDecodeError:
            pass

        # Try parsing line-by-line (NDJSON)
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                item = json.loads(line_str)
                if isinstance(item, dict):
                    records.append(self._extract_from_dict(item, idx + 1, filename, default_device))
            except Exception as e:
                records.append(RawEvidenceRecord(
                    timestamp_raw=None,
                    event_type="CORRUPT_JSON_LINE",
                    event_description=f"Line {idx+1} malformed JSON: {line_str[:100]}",
                    device=default_device,
                    source=filename,
                    source_record_id=str(idx + 1),
                    parsing_error=str(e)
                ))

        return records
