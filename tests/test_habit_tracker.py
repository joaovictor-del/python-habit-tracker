import tempfile
import unittest
from datetime import date
from pathlib import Path

from habit_tracker import active_streak, load_entries, record_habit, save_entries, summarize


class HabitTrackerTests(unittest.TestCase):
    def test_record_sorts_entries_and_uses_injected_today(self):
        entries = []
        record_habit(entries, "  Leitura ", today=date(2025, 1, 2))
        record_habit(entries, "Exercício", logged_on="2025-01-01", today=date(2025, 1, 2))
        self.assertEqual(
            entries,
            [
                {"habit": "Exercício", "date": "2025-01-01"},
                {"habit": "Leitura", "date": "2025-01-02"},
            ],
        )

    def test_duplicate_habit_on_same_day_is_rejected(self):
        entries = [{"habit": "Leitura", "date": "2025-01-02"}]
        with self.assertRaisesRegex(ValueError, "já foi registrado"):
            record_habit(entries, "Leitura", today=date(2025, 1, 2))

    def test_future_date_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "data futura"):
            record_habit([], "Leitura", "2025-01-03", today=date(2025, 1, 2))

    def test_active_streak_includes_yesterday_if_not_logged_today(self):
        entries = [
            {"habit": "Leitura", "date": "2025-01-01"},
            {"habit": "Leitura", "date": "2025-01-02"},
        ]
        self.assertEqual(active_streak(entries, "leitura", date(2025, 1, 3)), 2)

    def test_active_streak_stops_at_a_missed_day(self):
        entries = [
            {"habit": "Leitura", "date": "2025-01-01"},
            {"habit": "Leitura", "date": "2025-01-03"},
        ]
        self.assertEqual(active_streak(entries, "Leitura", date(2025, 1, 3)), 1)

    def test_summary_reports_count_and_streak(self):
        entries = [
            {"habit": "Leitura", "date": "2025-01-01"},
            {"habit": "Leitura", "date": "2025-01-02"},
            {"habit": "Alongamento", "date": "2025-01-02"},
        ]
        self.assertEqual(
            summarize(entries, date(2025, 1, 2)),
            [("Alongamento", 1, 1), ("Leitura", 2, 2)],
        )

    def test_entries_round_trip_through_json(self):
        entries = [{"habit": "Leitura", "date": "2025-01-02"}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "habits.json"
            save_entries(entries, path)
            self.assertEqual(load_entries(path), entries)


if __name__ == "__main__":
    unittest.main()
