from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class RawEvidenceRecord:
    timestamp_raw: Any
    event_type: str
    event_description: str
    device: str = "Unknown Device"
    source: str = "Generic Log"
    source_record_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    parsing_error: Optional[str] = None

class BaseProcessor(ABC):
    """Abstract base class for forensic evidence file parsers."""

    @abstractmethod
    def can_process(self, filename: str, content: bytes) -> bool:
        """Check if this processor can handle the given file."""
        pass

    @abstractmethod
    def parse(self, content: bytes, filename: str, default_device: str = "Unknown Device") -> List[RawEvidenceRecord]:
        """Parse raw file bytes into raw forensic records."""
        pass
