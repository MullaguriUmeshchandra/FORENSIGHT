import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from app.processors.base import BaseProcessor, RawEvidenceRecord

class XMLProcessor(BaseProcessor):
    """Processor for XML forensic exports and Windows Event Log XMLs."""

    def can_process(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".xml")

    def _elem_to_dict(self, elem: ET.Element) -> Dict[str, Any]:
        d = {}
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if len(child) > 0:
                d[tag] = self._elem_to_dict(child)
            else:
                d[tag] = child.text or ""
        # Also copy attributes
        for k, v in elem.attrib.items():
            attr_key = k.split("}")[-1] if "}" in k else k
            d[f"@{attr_key}"] = v
        return d

    def parse(self, content: bytes, filename: str, default_device: str = "Unknown Device") -> List[RawEvidenceRecord]:
        records: List[RawEvidenceRecord] = []
        try:
            # Parse XML securely
            parser = ET.XMLParser()
            root = ET.fromstring(content, parser=parser)
        except Exception as e:
            return [RawEvidenceRecord(
                timestamp_raw=None,
                event_type="CORRUPT_XML_ERROR",
                event_description=f"XML parsing failure: {str(e)}",
                device=default_device,
                source=filename,
                parsing_error=str(e)
            )]

        # Look for Event nodes
        events = root.findall(".//Event")
        if not events:
            # Try top-level children
            events = list(root)

        for idx, ev in enumerate(events):
            ed = self._elem_to_dict(ev)
            
            # Look for TimeCreated or System.TimeCreated
            ts = None
            if "System" in ed and isinstance(ed["System"], dict):
                sys_dict = ed["System"]
                ts = sys_dict.get("TimeCreated", {}).get("@SystemTime") or sys_dict.get("@SystemTime")
                computer = sys_dict.get("Computer") or default_device
                event_id = sys_dict.get("EventID") or f"Event-{idx+1}"
            else:
                computer = default_device
                event_id = f"Item-{idx+1}"

            # Fallback search for timestamp in any key
            if not ts:
                for k, v in ed.items():
                    if "time" in k.lower() or "date" in k.lower():
                        if isinstance(v, str):
                            ts = v
                            break

            desc = f"XML Event {event_id}"
            if "EventData" in ed:
                desc = f"{desc}: {str(ed['EventData'])[:200]}"

            records.append(RawEvidenceRecord(
                timestamp_raw=ts,
                event_type=f"XML_EVENT_{event_id}",
                event_description=desc,
                device=str(computer),
                source=filename,
                source_record_id=str(idx + 1),
                metadata=ed,
                confidence=1.0
            ))

        return records
