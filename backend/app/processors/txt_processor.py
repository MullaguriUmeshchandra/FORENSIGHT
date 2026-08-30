import re
from typing import List
from app.processors.base import BaseProcessor, RawEvidenceRecord

TIMESTAMP_REGEX = re.compile(
    r"(\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?|"
    r"[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
)

class TXTProcessor(BaseProcessor):
    """Processor for generic forensic text exports and notes."""

    def can_process(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".txt")

    def parse(self, content: bytes, filename: str, default_device: str = "Unknown Device") -> List[RawEvidenceRecord]:
        records: List[RawEvidenceRecord] = []
        text = content.decode("utf-8-sig", errors="replace")
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str:
                continue

            # Look for timestamp in line
            ts_match = TIMESTAMP_REGEX.search(line_str)
            if ts_match:
                ts_raw = ts_match.group(1)
                desc = line_str.replace(ts_raw, "").strip(" -|:,\t")
                if not desc:
                    desc = line_str
                records.append(RawEvidenceRecord(
                    timestamp_raw=ts_raw,
                    event_type="TEXT_LOG_ENTRY",
                    event_description=desc,
                    device=default_device,
                    source=filename,
                    source_record_id=str(idx + 1),
                    metadata={"raw_line": line_str},
                    confidence=0.9
                ))
            else:
                records.append(RawEvidenceRecord(
                    timestamp_raw=None,
                    event_type="TEXT_NOTE",
                    event_description=line_str,
                    device=default_device,
                    source=filename,
                    source_record_id=str(idx + 1),
                    metadata={"raw_line": line_str},
                    confidence=0.7
                ))

        return records
