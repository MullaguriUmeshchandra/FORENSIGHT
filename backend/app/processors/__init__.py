from typing import List
from .base import BaseProcessor, RawEvidenceRecord
from .csv_processor import CSVProcessor
from .json_processor import JSONProcessor
from .log_processor import LogProcessor
from .txt_processor import TXTProcessor
from .xml_processor import XMLProcessor

REGISTERED_PROCESSORS: List[BaseProcessor] = [
    CSVProcessor(),
    JSONProcessor(),
    LogProcessor(),
    TXTProcessor(),
    XMLProcessor(),
]

def get_processor_for_file(filename: str, content: bytes) -> BaseProcessor:
    """Select the best matching processor for a file format."""
    for proc in REGISTERED_PROCESSORS:
        if proc.can_process(filename, content):
            return proc
    # Default to TXT processor for arbitrary text/stream
    return TXTProcessor()

__all__ = [
    "BaseProcessor",
    "RawEvidenceRecord",
    "CSVProcessor",
    "JSONProcessor",
    "LogProcessor",
    "TXTProcessor",
    "XMLProcessor",
    "REGISTERED_PROCESSORS",
    "get_processor_for_file",
]
