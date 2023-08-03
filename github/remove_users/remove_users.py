import argparse
import logging
from requests_cache import CachedSession, SQLiteCache
import json
import os

from copy import deepcopy

logger = logging.getLogger('requests_cache')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


github_token = os.environ.get("GITHUB_TOKEN")
github_org = os.environ.get("GITHUB_ORG")
github_api_base_url = "https://api.github.com"

# Set up a cache with a time limit in seconds
backend = SQLiteCache()
session = CachedSession(
    allowable_methods=("GET",),
    backend=backend,
    expire_after=300
)


def parse_arguments():
    # Add users flag
    description = "List of users to be removed"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--users", nargs="+", help="The list of users", required=True
    )

    # Add the --dry-run flag
    parser.add_argument('--dry-run', action='store_true',
                        help='Enable dry-run mode')

    # Add the --ignore flag
    parser.add_argument('--ignore', nargs='+',
                        help='List of teams not to be checked', required=False)

    return parser.parse_args()


def get_headers():
    headers = {
        "Authorization": f"Bearer {github_token}"
    }
    return headers


def get_github_teams(test_payload: dict = None, headers: dict = get_headers()):
    if not test_payload:
        url = f"{github_api_base_url}/orgs/{github_org}/teams"
        response = session.get(
            url=url,
            headers=headers
        )
        status_code = response.status_code
        data = json.loads(response.text)
    else:
        status_code = 200
        data = test_payload

    if status_code == 200:
        teams = [team["slug"]for team in data]
        return teams

    if response.status_code == 401:
        logger.error(
            "Invalid Github credentials, set credentials using environment variable GITHUB_TOKEN")
        exit(1)

    if response.status_code == 404:
        logger.error(
            "Check GITHUB_ORG is correct, set credentials using environment variable GITHUB_ORG")
        logger.error(f"URL: {url}")
        exit(1)

    logger.error("Unable to process response received from Github")
    logger.error(
        f"status_code: {response.status_code}, message: {response.text}")
    return None


def remove_ignored_teams(ignored_teams: list, teams: list):
    try:
        _filtered_teams = deepcopy(teams)
        for team in ignored_teams:
            del _filtered_teams[_filtered_teams.index(team)]

        return _filtered_teams
    except ValueError:
        return _filtered_teams


def main():
    args = parse_arguments()
    users = args.users
    dry_run = args.dry_run
    ignored_teams = args.ignore
    all_teams = get_github_teams()
    teams = remove_ignored_teams(ignored_teams=ignored_teams, teams=all_teams)
    logger.info(f"Teams to check: {teams}")

    # Clear Cache
    # session.cache.clear()


if __name__ == "__main__":
    main()
