"""Command-line entry point for repodigest."""

import os
import sys

import click

from repodigest.digest import build_digest
from repodigest.formatter import format_digest
from repodigest.github_client import GitHubClient


@click.command()
@click.argument("repo", metavar="OWNER/REPO")
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    default=None,
    help="GitHub personal access token (or set GITHUB_TOKEN).",
)
@click.option(
    "--output",
    type=click.Path(writable=True),
    default=None,
    help="Write digest to FILE instead of stdout.",
)
def main(repo: str, token: str | None, output: str | None) -> None:
    """Generate a weekly activity digest for OWNER/REPO."""
    if "/" not in repo:
        click.echo("Error: REPO must be in OWNER/REPO format.", err=True)
        sys.exit(1)

    owner, repo_name = repo.split("/", 1)
    client = GitHubClient(token=token or os.environ.get("GITHUB_TOKEN"))

    try:
        digest = build_digest(owner, repo_name, client)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error fetching data: {exc}", err=True)
        sys.exit(1)

    summary = format_digest(digest)

    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(summary + "\n")
        click.echo(f"Digest written to {output}")
    else:
        click.echo(summary)


if __name__ == "__main__":
    main()
