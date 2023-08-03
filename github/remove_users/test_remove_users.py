from remove_users import parse_arguments, get_github_teams, remove_ignored_teams

import pytest
import json
import responses
import os


# Users
def load_dataset(file_name: str):
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the JSON file
    json_file_path = os.path.join(script_dir, file_name)

    # Open the JSON file
    with open(json_file_path, "r") as json_file:
        # Load the contents of the JSON file
        data = json.load(json_file)

    return data


def test_parse_arguments(monkeypatch):
    # Test case: Valid user list
    monkeypatch.setattr(
        "sys.argv", ["remove_users.py", "--users", "user1", "user2"])
    args = parse_arguments()
    assert args.users == ["user1", "user2"]

    # Test case 2: Empty user list
    monkeypatch.setattr("sys.argv", ["remove_users.py", "--users"])
    with pytest.raises(SystemExit):
        parse_arguments()

    # Test case 3: Missing user list
    monkeypatch.setattr("sys.argv", ["remove_users.py"])
    with pytest.raises(SystemExit):
        parse_arguments()


def test_dry_run_disabled(monkeypatch):
    # Set the command-line arguments to simulate dry-run being disabled
    monkeypatch.setattr(
        "sys.argv", ["remove_users.py", "--users", "user1", "user2"]
    )

    # Parse the arguments
    parsed_args = parse_arguments()

    # Assert that the dry-run flag is False
    assert parsed_args.dry_run is False


def test_dry_run_enabled(monkeypatch):
    # Set the command-line arguments to simulate dry-run being disabled
    monkeypatch.setattr(
        "sys.argv", ["remove_users.py",
                     "--users", "user1", "user2",
                     "--dry-run"]
    )

    # Parse the arguments
    parsed_args = parse_arguments()

    # Assert that the dry-run flag is False
    assert parsed_args.dry_run


def test_ignore_flag_empty_by_default(monkeypatch):
    # Set the command-line arguments to simulate an empty --ignore flag
    monkeypatch.setattr(
        "sys.argv", ["remove_users.py",
                     "--users", "user1", "user2"]
    )

    # Parse the arguments
    parsed_args = parse_arguments()

    # Assert that the ignore flag is None
    assert parsed_args.ignore is None


def test_ignore_flag_empty(monkeypatch):
    # Set the command-line arguments to simulate an empty --ignore flag
    monkeypatch.setattr(
        'sys.argv', ["remove_users.py", "--users", "user1", "user2", "--ignore", ""])

    # Parse the arguments
    parsed_args = parse_arguments()

    # Assert that the ignore flag is None
    assert parsed_args.ignore == [""]


# Get GitHub teams
def test_get_github_teams():
    test_payload = load_dataset(file_name="responses/teams.json")

    teams = get_github_teams(test_payload=test_payload)

    assert len(teams) == 3
    assert teams == ["test-admins", "test-developers", "test-ops"]


def test_remove_ignored_teams_success():
    teams = ["test-admins", "test-developers", "test-ops"]
    ignored_teams = ["test-ops"]

    result = remove_ignored_teams(ignored_teams=ignored_teams, teams=teams)

    assert result == ["test-admins", "test-developers"]


def test_remove_ignored_teams_when_ignored_teams_is_empty():
    teams = ["test-admins", "test-developers", "test-ops"]
    ignored_teams = []

    result = remove_ignored_teams(ignored_teams=ignored_teams, teams=teams)

    assert result == teams


@pytest.mark.smoke
def test_remove_ignored_teams_when_teams_is_empty():
    teams = []
    ignored_teams = ["test"]

    result = remove_ignored_teams(ignored_teams=ignored_teams, teams=teams)

    assert result == teams
