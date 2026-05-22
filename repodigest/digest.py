"""Build a structured digest from raw GitHub API data."""

from dataclasses import dataclass, field
from datetime import datetime

from repodigest.github_client import GitHubClient, week_ago


@dataclass
class Digest:
    owner: str
    repo: str
    since: datetime
    commits: list[dict] = field(default_factory=list)
    pull_requests: list[dict] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)
    releases: list[dict] = field(default_factory=list)

    @property
    def commit_count(self) -> int:
        return len(self.commits)

    @property
    def open_prs(self) -> list[dict]:
        return [pr for pr in self.pull_requests if pr["state"] == "open"]

    @property
    def merged_prs(self) -> list[dict]:
        return [pr for pr in self.pull_requests if pr.get("merged_at")]

    @property
    def open_issues(self) -> list[dict]:
        return [i for i in self.issues if i["state"] == "open"]

    @property
    def closed_issues(self) -> list[dict]:
        return [i for i in self.issues if i["state"] == "closed"]

    @property
    def latest_release(self) -> dict | None:
        return self.releases[0] if self.releases else None


def build_digest(owner: str, repo: str, client: GitHubClient, since: datetime | None = None) -> Digest:
    """Fetch all activity and return a populated Digest."""
    since = since or week_ago()
    digest = Digest(owner=owner, repo=repo, since=since)
    digest.commits = client.get_commits(owner, repo, since)
    digest.pull_requests = client.get_pull_requests(owner, repo, since)
    digest.issues = client.get_issues(owner, repo, since)
    digest.releases = client.get_releases(owner, repo)
    return digest
