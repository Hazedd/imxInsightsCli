from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class GitHubRelease:
    owner: str
    repo: str
    name: str
    tag_name: str
    published_at: str


def get_latest_release_github(repo_owner: str, repo_name: str) -> Optional[GitHubRelease]:
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            release_info = response.json()
            return GitHubRelease(
                owner=repo_owner, repo=repo_name,
                name=release_info['name'], tag_name=release_info['tag_name'], published_at=release_info['published_at']
            )
        else:
            return None
    except Exception as e:
        _ = e
        return None


if __name__ == "__main__":
    owner = "Hazedd"
    repo = "imxInsightsCli"

    latest_release = get_latest_release_github(owner, repo)
    print(latest_release)
