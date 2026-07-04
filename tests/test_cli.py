"""Tests for the sqlalchemyseed command-line interface."""

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemyseed import cli
from tests.models import Base, Person


@pytest.fixture
def db_url(tmp_path):
    """A file-backed SQLite URL with the test schema already created."""
    url = f"sqlite:///{tmp_path / 'seed.db'}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    engine.dispose()
    return url


def count_persons(url):
    with Session(create_engine(url)) as session:
        return session.query(Person).count()


def write_json(path, entities):
    path.write_text(json.dumps(entities), encoding="utf-8")
    return path


def person_entities(*names):
    return {"model": "tests.models.Person", "data": [{"name": name} for name in names]}


def test_seed_json_file(tmp_path, db_url):
    data_file = write_json(tmp_path / "people.json", person_entities("Alice", "Bob"))

    assert cli.main([str(data_file), "--url", db_url]) == 0
    assert count_persons(db_url) == 2


def test_seed_yaml_file(tmp_path, db_url):
    yaml_file = tmp_path / "people.yaml"
    yaml_file.write_text(
        "model: tests.models.Person\ndata:\n  - name: Carol\n", encoding="utf-8"
    )

    assert cli.main([str(yaml_file), "--url", db_url]) == 0
    assert count_persons(db_url) == 1


def test_seed_csv_file_requires_model(tmp_path, db_url):
    csv_file = tmp_path / "people.csv"
    csv_file.write_text("name\nDave\nErin\n", encoding="utf-8")

    exit_code = cli.main(
        [str(csv_file), "--url", db_url, "--model", "tests.models.Person"]
    )

    assert exit_code == 0
    assert count_persons(db_url) == 2


def test_csv_without_model_fails(tmp_path, db_url, capsys):
    csv_file = tmp_path / "people.csv"
    csv_file.write_text("name\nDave\n", encoding="utf-8")

    assert cli.main([str(csv_file), "--url", db_url]) == 1
    assert "requires a model" in capsys.readouterr().err
    assert count_persons(db_url) == 0


def test_seed_directory(tmp_path, db_url):
    seeds = tmp_path / "seeds"
    seeds.mkdir()
    write_json(seeds / "01_first.json", person_entities("Alice"))
    write_json(seeds / "02_second.json", person_entities("Bob", "Carol"))

    assert cli.main([str(seeds), "--url", db_url]) == 0
    assert count_persons(db_url) == 3


def test_multiple_paths(tmp_path, db_url):
    first = write_json(tmp_path / "a.json", person_entities("Alice"))
    second = write_json(tmp_path / "b.json", person_entities("Bob"))

    assert cli.main([str(first), str(second), "--url", db_url]) == 0
    assert count_persons(db_url) == 2


def test_dry_run_rolls_back(tmp_path, db_url, capsys):
    data_file = write_json(tmp_path / "people.json", person_entities("Alice", "Bob"))

    assert cli.main([str(data_file), "--url", db_url, "--dry-run"]) == 0
    assert "Dry run" in capsys.readouterr().out
    assert count_persons(db_url) == 0


def test_hybrid_seeder(tmp_path, db_url):
    data_file = write_json(tmp_path / "people.json", person_entities("Alice"))

    assert cli.main([str(data_file), "--url", db_url, "--seeder", "hybrid"]) == 0
    assert count_persons(db_url) == 1


def test_url_from_environment(tmp_path, db_url, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", db_url)
    data_file = write_json(tmp_path / "people.json", person_entities("Alice"))

    assert cli.main([str(data_file)]) == 0
    assert count_persons(db_url) == 1


def test_missing_url_errors(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    data_file = write_json(tmp_path / "people.json", person_entities("Alice"))

    with pytest.raises(SystemExit):
        cli.main([str(data_file)])


def test_nonexistent_path_errors(db_url):
    with pytest.raises(SystemExit):
        cli.main(["does_not_exist.json", "--url", db_url])


def test_unsupported_file_type(tmp_path, db_url):
    bad_file = tmp_path / "people.txt"
    bad_file.write_text("nope", encoding="utf-8")

    assert cli.main([str(bad_file), "--url", db_url]) == 1


def test_error_message_includes_exception_type(tmp_path, db_url, capsys):
    bad_file = tmp_path / "people.txt"
    bad_file.write_text("nope", encoding="utf-8")

    assert cli.main([str(bad_file), "--url", db_url]) == 1
    assert "ValueError" in capsys.readouterr().err


def test_debug_flag_reraises_with_traceback(tmp_path, db_url):
    bad_file = tmp_path / "people.txt"
    bad_file.write_text("nope", encoding="utf-8")

    with pytest.raises(ValueError):
        cli.main([str(bad_file), "--url", db_url, "--debug"])
