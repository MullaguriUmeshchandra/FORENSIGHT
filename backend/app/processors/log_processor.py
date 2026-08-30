import re
from typing import List
from app.processors.base import BaseProcessor, RawEvidenceRecord

SYSLOG_PATTERN = re.compile(r"^([A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+([^\s]+)\s+([^:]+):\s+(.*)$")
ISO_LOG_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s*(?:\[([^\]]+)\]|\(([^\)]+)\)|(\S+))?\s*(.*)$")
APACHE_LOG_PATTERN = re.compile(r"^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+\"([^\"]+)\"\s+(\d{3})\s+(\S+)")

class LogProcessor(BaseProcessor):
    """Processor for syslog, web server, and standard system log files."""

    def can_process(self, filename: str, content: bytes) -> bool:
        fn = filename.lower()
        return fn.endswith(".log")

    def parse(self, content: bytes, filename: str, default_device: str = "Unknown Device") -> List[RawEvidenceRecord]:
        records: List[RawEvidenceRecord] = []
        text = content.decode("utf-8-sig", errors="replace")
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str:
                continue

            # 1. Try ISO log pattern
            iso_match = ISO_LOG_PATTERN.match(line_str)
            if iso_match:
                ts, tag1, tag2, tag3, msg = iso_match.groups()
                tag = tag1 or tag2 or tag3 or "SYSTEM_LOG"
                records.append(RawEvidenceRecord(
                    timestamp_raw=ts,
                    event_type=tag.strip(),
                    event_description=msg.strip() if msg else line_str,
                    device=default_device,
                    source=filename,
                    source_record_id=str(idx + 1),
                    metadata={"raw_line": line_str},
                    confidence=1.0
                ))
                continue

            # 2. Try Syslog pattern
            syslog_match = SYSLOG_PATTERN.match(line_str)
            if syslog_match:
                ts, host, tag, msg = syslog_match.groups()
                records.append(RawEvidenceRecord(
                    timestamp_raw=ts,
                    event_type=tag.strip(),
                    event_description=msg.strip(),
                    device=host.strip() or default_device,
                    source=filename,
                    source_record_id=str(idx + 1),
                    metadata={"raw_line": line_str},
                    confidence=1.0
                ))
                continue

            # 3. Try Apache/Nginx pattern
            apache_match = APACHE_LOG_PATTERN.match(line_str)
            if apache_match:
                ip, ts, req, status, size = apache_match.groups()
                records.append(RawEvidenceRecord(
                    timestamp_raw=ts,
                    event_type="HTTP_REQUEST",
                    event_description=f"{req} (Status: {status}, Size: {size})",
                    device=ip.strip() or default_device,
                    source=filename,
                    source_record_id=str(idx + 1),
                    metadata={"ip": ip, "status": status, "size": size, "raw_line": line_str},
                    confidence=1.0
                ))
                continue

            # Generic fallback
            records.append(RawEvidenceRecord(
                timestamp_raw=None,
                event_type="UNSTRUCTURED_LOG_LINE",
                event_description=line_str,
                device=default_device,
                source=filename,
                source_record_id=str(idx + 1),
                metadata={"raw_line": line_str},
                confidence=0.8
            ))

        return records
