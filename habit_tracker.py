"""Registra hábitos e acompanha sequências de dias consecutivos."""

import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Optional


Entry = dict[str, str]


def load_entries(path: Path) -> list[Entry]:
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or any(
        not isinstance(entry, dict)
        or not isinstance(entry.get("habit"), str)
        or not entry["habit"].strip()
        or not isinstance(entry.get("date"), str)
        for entry in data
    ):
        raise ValueError(f"Formato de registros inválido em {path}")

    entries = []
    for entry in data:
        try:
            date.fromisoformat(entry["date"])
        except ValueError as error:
            raise ValueError(f"Data inválida em {path}: {entry['date']}") from error
        entries.append({"habit": entry["habit"], "date": entry["date"]})
    return entries


def save_entries(entries: list[Entry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def record_habit(
    entries: list[Entry],
    habit: str,
    logged_on: Optional[str] = None,
    today: Optional[date] = None,
) -> Entry:
    habit = habit.strip()
    if not habit:
        raise ValueError("O nome do hábito não pode ficar vazio.")

    try:
        logged_date = date.fromisoformat(logged_on) if logged_on else (today or date.today())
    except ValueError as error:
        raise ValueError("A data deve estar no formato AAAA-MM-DD.") from error

    if logged_date > (today or date.today()):
        raise ValueError("Não é possível registrar um hábito em uma data futura.")

    entry = {"habit": habit, "date": logged_date.isoformat()}
    if entry in entries:
        raise ValueError(f"{habit} já foi registrado em {entry['date']}.")

    entries.append(entry)
    entries.sort(key=lambda item: (item["date"], item["habit"].casefold()))
    return entry


def active_streak(
    entries: list[Entry], habit: str, today: Optional[date] = None
) -> int:
    reference = today or date.today()
    logged_dates = {
        date.fromisoformat(entry["date"])
        for entry in entries
        if entry["habit"].casefold() == habit.casefold()
    }

    if reference not in logged_dates:
        reference -= timedelta(days=1)
    streak = 0
    while reference in logged_dates:
        streak += 1
        reference -= timedelta(days=1)
    return streak


def summarize(entries: list[Entry], today: Optional[date] = None) -> list[tuple[str, int, int]]:
    habits = sorted({entry["habit"] for entry in entries}, key=str.casefold)
    return [
        (
            habit,
            sum(entry["habit"].casefold() == habit.casefold() for entry in entries),
            active_streak(entries, habit, today),
        )
        for habit in habits
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Registre hábitos e acompanhe sua consistência.")
    parser.add_argument("--file", type=Path, default=Path("habits.json"))
    commands = parser.add_subparsers(dest="command", required=True)

    log_parser = commands.add_parser("log", help="registra um hábito")
    log_parser.add_argument("habit")
    log_parser.add_argument("--date", dest="logged_on", help="data no formato AAAA-MM-DD")
    commands.add_parser("history", help="mostra todos os registros")
    commands.add_parser("summary", help="resume frequência e sequência atual")
    args = parser.parse_args()

    entries = load_entries(args.file)
    if args.command == "log":
        entry = record_habit(entries, args.habit, args.logged_on)
        save_entries(entries, args.file)
        print(f"{entry['habit']} registrado em {entry['date']}.")
    elif args.command == "history":
        if not entries:
            print("Nenhum hábito registrado.")
        for entry in entries:
            print(f"{entry['date']} | {entry['habit']}")
    else:
        summary = summarize(entries)
        if not summary:
            print("Nenhum hábito registrado.")
        for habit, total, streak in summary:
            print(f"{habit}: {total} registro(s) | sequência atual: {streak} dia(s)")


if __name__ == "__main__":
    main()
