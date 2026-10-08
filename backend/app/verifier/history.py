"""
Persistent Verification Log & Timeline Charting Manager for Module 7 (RASR).
Stores verification results to JSON and provides structured timeline data for dashboard charting.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from app.schemas.verifier import VerificationReport, VerificationChartData

logger = logging.getLogger(__name__)

VERIFICATION_LOG_FILE = Path(__file__).resolve().parent.parent / "core" / "verification_history.json"


class VerificationLogManager:
    """
    Manages persistent logging and timeline metric retrieval of patch verification runs.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or VERIFICATION_LOG_FILE
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.storage_path.exists():
            try:
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.storage_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
            except Exception as e:
                logger.error(f"[VerificationLogManager] Error creating history storage: {e}")

    def log_report(self, report: VerificationReport) -> None:
        """Appends a new verification report to persistent storage."""
        try:
            self._ensure_storage()
            records = self.get_all_reports()
            records.append(report.model_dump())
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
            logger.info(f"[VerificationLogManager] Logged verification '{report.verification_id}' for patch '{report.patch_id}' (RASR: {report.overall_rasr:.1%}).")
        except Exception as e:
            logger.error(f"[VerificationLogManager] Failed to write verification log: {e}")

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Retrieves all logged verification records."""
        if not self.storage_path.exists():
            return []
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[VerificationLogManager] Error reading verification history: {e}")
            return []

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        records = self.get_all_reports()
        return records[-1] if records else None

    def get_next_patch_index(self) -> int:
        records = self.get_all_reports()
        return len(records) + 1

    def get_chart_data(self) -> VerificationChartData:
        """
        Synthesizes longitudinal timeline series for rendering the headline RASR reduction chart:
        Patch #1 -> RASR, Patch #2 -> RASR, ...
        """
        records = self.get_all_reports()
        if not records:
            return VerificationChartData(
                timeline=[],
                current_rasr=0.0,
                total_patches_verified=0,
                fully_mitigated_count=0,
                average_mitigation_rate=0.0,
                category_averages={}
            )

        timeline = []
        category_totals: Dict[str, List[float]] = {}
        fully_mitigated_count = 0

        for r in records:
            idx = r.get("patch_index", len(timeline) + 1)
            overall_rasr = r.get("overall_rasr", 0.0)
            primary_cat = r.get("primary_category", "unknown")
            primary_rasr = r.get("primary_category_rasr", overall_rasr)
            cross_cats = r.get("cross_category_rasrs", {})

            cat_breakdown = {primary_cat: primary_rasr}
            for cat_key, cat_data in cross_cats.items():
                cat_rasr = cat_data.get("rasr", 0.0) if isinstance(cat_data, dict) else cat_data
                cat_breakdown[cat_key] = cat_rasr

            for k, val in cat_breakdown.items():
                category_totals.setdefault(k, []).append(val)

            if r.get("verdict") == "fully_mitigated" or overall_rasr == 0.0:
                fully_mitigated_count += 1

            timeline.append({
                "patch_index": idx,
                "label": f"Patch #{idx}",
                "patch_id": r.get("patch_id"),
                "patch_type": r.get("patch_type"),
                "timestamp": r.get("timestamp"),
                "primary_category": primary_cat,
                "primary_rasr": round(primary_rasr, 4),
                "overall_rasr": round(overall_rasr, 4),
                "mitigation_rate": round(r.get("mitigation_rate", 1.0 - overall_rasr), 4),
                "verdict": r.get("verdict", "fully_mitigated"),
                "category_breakdown": cat_breakdown,
                "replayed_probes_count": r.get("replayed_probes_count", 0)
            })

        latest_record = records[-1]
        category_averages = {
            k: round(sum(vals) / len(vals), 4) for k, vals in category_totals.items() if vals
        }
        avg_mitigation = round(
            sum(r.get("mitigation_rate", 1.0 - r.get("overall_rasr", 0.0)) for r in records) / len(records),
            4
        )

        return VerificationChartData(
            timeline=timeline,
            current_rasr=latest_record.get("overall_rasr", 0.0),
            total_patches_verified=len(records),
            fully_mitigated_count=fully_mitigated_count,
            average_mitigation_rate=avg_mitigation,
            category_averages=category_averages
        )

    def reset(self) -> None:
        """Clears all verification history."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
            logger.info("[VerificationLogManager] Cleared verification history.")
        except Exception as e:
            logger.error(f"[VerificationLogManager] Failed to reset history: {e}")


verification_log_manager = VerificationLogManager()
