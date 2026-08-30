import io
import csv
import pandas as pd
from typing import List, Dict, Any, Optional
from app.processors.base import BaseProcessor, RawEvidenceRecord
from app.utils.logger import logger

TIMESTAMP_HEADERS = ["timestamp", "time", "date", "datetime", "event_time", "logged_at", "timecreated", "created_at", "time_generated"]
EVENT_DESC_HEADERS = ["event_description", "description", "event", "action", "message", "activity", "details", "query", "url", "file_name", "path"]
EVENT_TYPE_HEADERS = ["event_type", "type", "action_type", "category", "source_type", "operation", "eventid", "event_id"]
DEVICE_HEADERS = ["device", "hostname", "host", "computer_name", "computer", "machine", "ip", "source_ip"]
ID_HEADERS = ["id", "record_id", "event_id", "row_id", "entry_id"]

class CSVProcessor(BaseProcessor):
    """Processor for CSV forensic logs."""

    def can_process(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".csv")

    def _find_matching_col(self, columns: List[str], candidates: List[str]) -> Optional[str]:
        cols_lower = {col.lower().strip().replace(" ", "_"): col for col in columns}
        for cand in candidates:
            if cand in cols_lower:
                return cols_lower[cand]
        # Partial match
        for cand in candidates:
            for c_low, original in cols_lower.items():
                if cand in c_low:
                    return original
        return None

    def parse(self, content: bytes, filename: str, default_device: str = "Unknown Device") -> List[RawEvidenceRecord]:
        records: List[RawEvidenceRecord] = []
        try:
            # Decode bytes to text
            text = content.decode("utf-8-sig", errors="replace")
            # Read CSV with pandas or csv
            df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
        except Exception as e:
            logger.error(f"Failed to read CSV in {filename}: {e}")
            return [RawEvidenceRecord(
                timestamp_raw=None,
                event_type="CORRUPT_CSV_PARSE_ERROR",
                event_description=f"CSV file could not be parsed: {str(e)}",
                device=default_device,
                source=filename,
                parsing_error=str(e)
            )]

        columns = list(df.columns)
        ts_col = self._find_matching_col(columns, TIMESTAMP_HEADERS)
        desc_col = self._find_matching_col(columns, EVENT_DESC_HEADERS)
        type_col = self._find_matching_col(columns, EVENT_TYPE_HEADERS)
        dev_col = self._find_matching_col(columns, DEVICE_HEADERS)
        id_col = self._find_matching_col(columns, ID_HEADERS)

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            ts_val = row_dict.get(ts_col) if ts_col else None
            
            # If date and time are in separate columns
            if not ts_val and "date" in [c.lower() for c in columns] and "time" in [c.lower() for c in columns]:
                d_col = [c for c in columns if c.lower() == "date"][0]
                t_col = [c for c in columns if c.lower() == "time"][0]
                ts_val = f"{row_dict.get(d_col, '')} {row_dict.get(t_col, '')}".strip()

            desc_val = row_dict.get(desc_col) if desc_col else None
            if not desc_val:
                # Construct description from non-timestamp fields
                desc_parts = [f"{k}: {v}" for k, v in row_dict.items() if k != ts_col and v]
                desc_val = ", ".join(desc_parts) if desc_parts else f"Row {idx+1} in {filename}"

            type_val = row_dict.get(type_col) if type_col else None
            if not type_val:
                type_val = filename.replace(".csv", "").upper().replace("SAMPLE_", "").replace("_LOGS", "")

            device_val = row_dict.get(dev_col) if dev_col else default_device
            if not device_val or device_val.strip() == "":
                device_val = default_device

            record_id = row_dict.get(id_col) if id_col else str(idx + 1)

            records.append(RawEvidenceRecord(
                timestamp_raw=ts_val,
                event_type=str(type_val).strip(),
                event_description=str(desc_val).strip(),
                device=str(device_val).strip(),
                source=filename,
                source_record_id=str(record_id),
                metadata=row_dict,
                confidence=1.0
            ))

        return records
