"""Command-line interface for seeding a database from data files."""

import argparse
import os
import sys
from pathlib import Path

import sqlalchemy
from sqlalchemy.orm import Session

from . import loader
from .seeder import HybridSeeder, Seeder


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``sqlalchemyseed`` command."""
    parser = argparse.ArgumentParser(
        prog="sqlalchemyseed",
        description="Seed a database from JSON, YAML, or CSV data files.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATH",
        help="data files or directories to seed from",
    )
    parser.add_argument(
        "--url",
        help="SQLAlchemy database URL (defaults to the DATABASE_URL env var)",
    )
    parser.add_argument(
        "--seeder",
        choices=("basic", "hybrid"),
        default="basic",
        help="seeder to use (default: basic)",
    )
    parser.add_argument(
        "--model",
        help="model class path (e.g. models.Person) required for CSV inputs",
    )
    parser.add_argument(
        "--ref-prefix",
        default="!",
        help="prefix marking relationship references (default: !)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="seed within a transaction but roll back instead of committing",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="re-raise errors with a full traceback instead of a one-line message",
    )
    return parser


def collect_files(paths) -> list:
    """Expand each path into data files, walking directories in sorted order."""
    files = []
    for raw_path in paths:
        files.extend(_files_in(Path(raw_path)))
    return files


def _files_in(path: Path) -> list:
    """Return the data files contributed by a single path argument."""
    if path.is_dir():
        return _discover_directory(path)
    if path.is_file():
        return [path]
    raise FileNotFoundError(f"path does not exist: {path}")


def _discover_directory(directory: Path) -> list:
    """Return the JSON/YAML files inside a directory, sorted by name."""
    discovered = sorted(
        child for child in directory.iterdir()
        if child.suffix.lower() in loader.DISCOVERABLE_EXTENSIONS
    )
    if not discovered:
        raise FileNotFoundError(
            f"no JSON or YAML seed files found in directory: {directory}"
        )
    return discovered


def _make_seeder(name, session, ref_prefix):
    """Return the seeder implementation selected on the command line."""
    if name == "hybrid":
        return HybridSeeder(session, ref_prefix=ref_prefix)
    return Seeder(session, ref_prefix=ref_prefix)


def _seed_all(seeder, files, model) -> int:
    """Seed every file through the seeder and return the entity count."""
    seeded = 0
    for path in files:
        seeder.seed(loader.load_path(path, model))
        seeded += len(seeder.instances)
    return seeded


def main(argv=None) -> int:
    """Entry point for the ``sqlalchemyseed`` command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    url = args.url or os.environ.get("DATABASE_URL")
    if not url:
        parser.error("a database URL is required via --url or the DATABASE_URL env var")

    # Make the caller's project importable so model paths like "models.Person"
    # resolve against the current working directory.
    sys.path.insert(0, os.getcwd())

    try:
        files = collect_files(args.paths)
    except FileNotFoundError as error:
        parser.error(str(error))

    try:
        engine = sqlalchemy.create_engine(url)
        with Session(engine) as session:
            seeder = _make_seeder(args.seeder, session, args.ref_prefix)
            seeded = _seed_all(seeder, files, args.model)
            return _finish(session, seeded, len(files), args.dry_run)
    except Exception as error:  # noqa: BLE001 - top-level boundary: report any failure as exit code 1
        if args.debug:
            raise
        print(f"error: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


def _finish(session, seeded, file_count, dry_run) -> int:
    """Commit or roll back the seeded session and print a summary."""
    if dry_run:
        session.rollback()
        print(f"Dry run: would seed {seeded} entities from {file_count} file(s) (rolled back).")
        return 0
    session.commit()
    print(f"Seeded {seeded} entities from {file_count} file(s).")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
