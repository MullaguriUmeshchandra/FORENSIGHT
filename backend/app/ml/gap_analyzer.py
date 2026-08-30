from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from app.models.gap import GapSeverity, GapType

def evaluate_gap_severity(duration_seconds: int) -> Tuple[GapSeverity, bool]:
    """
    Evaluate gap severity based on actual forensic thresholds:
    - Less than 2 minutes (120s): Ignore (return None, False)
    - 2-5 minutes (120s - 300s): Low
    - 5-15 minutes (300s - 900s): Medium
    - More than 15 minutes (> 900s): High
    """
    if duration_seconds < 120:
        return GapSeverity.LOW, False  # Ignore
    elif 120 <= duration_seconds < 300:
        return GapSeverity.LOW, True
    elif 300 <= duration_seconds < 900:
        return GapSeverity.MEDIUM, True
    else:
        return GapSeverity.HIGH, True

def format_duration(seconds: int) -> str:
    """Format duration seconds into human readable format: e.g. 13m 00s, 1h 05m 20s."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs:02d}s")
    return " ".join(parts)

class GapAnalyzer:
    """Forensic Gap Analyzer with Isolation Forest temporal anomaly scoring."""

    @staticmethod
    def detect_time_gaps(events: List[Any]) -> List[Dict[str, Any]]:
        """
        Analyze chronological events and detect unexplained time transitions.
        Uses scikit-learn Isolation Forest to score time delta anomalies objectively.
        """
        gaps: List[Dict[str, Any]] = []
        if len(events) < 2:
            return gaps

        sorted_events = sorted(events, key=lambda x: x.timestamp)
        deltas = []
        event_pairs = []

        for i in range(len(sorted_events) - 1):
            prev_ev = sorted_events[i]
            next_ev = sorted_events[i + 1]

            t1: datetime = prev_ev.timestamp
            t2: datetime = next_ev.timestamp

            if t2 < t1:
                continue

            delta_seconds = int((t2 - t1).total_seconds())
            deltas.append(delta_seconds)
            event_pairs.append((prev_ev, next_ev, delta_seconds))

        if not deltas:
            return gaps

        # Use Isolation Forest if enough data points, otherwise threshold evaluation
        anomaly_scores = [1.0] * len(deltas)
        if len(deltas) >= 4:
            try:
                X = np.array(deltas).reshape(-1, 1)
                clf = IsolationForest(contamination=0.2, random_state=42)
                clf.fit(X)
                raw_scores = clf.score_samples(X) # Higher = normal, Lower = anomaly
                # Normalize confidence score
                min_s, max_s = min(raw_scores), max(raw_scores)
                if max_s > min_s:
                    anomaly_scores = [float(0.5 + 0.5 * (s - min_s) / (max_s - min_s)) for s in raw_scores]
            except Exception:
                pass

        for idx, (prev_ev, next_ev, delta_seconds) in enumerate(event_pairs):
            severity, is_significant = evaluate_gap_severity(delta_seconds)

            if is_significant:
                dur_str = format_duration(delta_seconds)
                t1_str = prev_ev.timestamp.strftime("%H:%M:%S")
                t2_str = next_ev.timestamp.strftime("%H:%M:%S")
                
                reason = (
                    f"An unexplained transition exists between {t1_str} and {t2_str} "
                    f"(duration: {dur_str}) between event '{prev_ev.event[:40]}' "
                    f"and '{next_ev.event[:40]}'."
                )

                gaps.append({
                    "start_time": prev_ev.timestamp,
                    "end_time": next_ev.timestamp,
                    "duration_seconds": delta_seconds,
                    "previous_event_id": prev_ev.id,
                    "next_event_id": next_ev.id,
                    "severity": severity,
                    "gap_type": GapType.UNEXPLAINED_TIME_GAP,
                    "reason": reason,
                    "confidence": round(anomaly_scores[idx], 2)
                })

        return gaps

    @staticmethod
    def detect_sequence_anomalies(events: List[Any]) -> List[Dict[str, Any]]:
        """
        Analyze typical state transitions (Login -> Interactive Activity -> Sensitive Access)
        and detect absent prerequisites without fabricating events.
        """
        sequence_gaps: List[Dict[str, Any]] = []
        if not events:
            return sequence_gaps

        sorted_events = sorted(events, key=lambda x: x.timestamp)
        event_texts_lower = [e.event.lower() for e in sorted_events]

        has_login = any("login" in txt or "logon" in txt or "session start" in txt for txt in event_texts_lower)
        has_privileged_action = any("file access" in txt or "exfiltration" in txt or "usb" in txt or "export" in txt for txt in event_texts_lower)

        if has_privileged_action and not has_login:
            first_action = sorted_events[0]
            reason = (
                "Expected session-start evidence was not found prior to observed interactive activity. "
                "No authentication logs exist for this session window."
            )
            sequence_gaps.append({
                "start_time": first_action.timestamp,
                "end_time": first_action.timestamp,
                "duration_seconds": 0,
                "previous_event_id": None,
                "next_event_id": first_action.id,
                "severity": GapSeverity.MEDIUM,
                "gap_type": GapType.MISSING_EXPECTED_EVENT,
                "reason": reason,
                "confidence": 0.95
            })

        return sequence_gaps
