from datetime import datetime, timezone
from app.utils.time_utils import parse_forensic_timestamp
from app.processors import get_processor_for_file

def test_timestamp_parsing_formats():
    # ISO-8601
    dt1 = parse_forensic_timestamp("2026-08-30T10:15:00Z")
    assert dt1 is not None
    assert dt1.hour == 10 and dt1.minute == 15
    assert dt1.tzinfo == timezone.utc

    # Standard format
    dt2 = parse_forensic_timestamp("2026-08-30 10:28:15")
    assert dt2 is not None
    assert dt2.minute == 28 and dt2.second == 15

    # Unix Epoch seconds
    dt3 = parse_forensic_timestamp(1788084900)  # timestamp in 2026
    assert dt3 is not None
    assert dt3.year == 2026

    # Invalid timestamp returns None (does not crash)
    dt_inv = parse_forensic_timestamp("invalid-date-string-xyz")
    assert dt_inv is None

def test_processors_multi_format():
    # 1. CSV
    csv_bytes = b"timestamp,event_type,device,action\n2026-08-30 10:15:00,LOGON,HOST-1,User authenticated\n"
    csv_proc = get_processor_for_file("log.csv", csv_bytes)
    csv_recs = csv_proc.parse(csv_bytes, "log.csv")
    assert len(csv_recs) == 1
    assert csv_recs[0].event_type == "LOGON"

    # 2. JSON
    json_bytes = b'[{"timestamp": "2026-08-30T10:21:00Z", "event": "Browser start", "device": "HOST-1"}]'
    json_proc = get_processor_for_file("browser.json", json_bytes)
    json_recs = json_proc.parse(json_bytes, "browser.json")
    assert len(json_recs) == 1
    assert "Browser start" in json_recs[0].event_description

    # 3. Log
    log_bytes = b"2026-08-30 10:28:00 INFO [System] USB storage device attached\n"
    log_proc = get_processor_for_file("system.log", log_bytes)
    log_recs = log_proc.parse(log_bytes, "system.log")
    assert len(log_recs) == 1
    assert "USB storage device" in log_recs[0].event_description
