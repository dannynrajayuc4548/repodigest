"""Render a Digest as a human-readable text summary."""

from repodigest.digest import Digest

SEP = "-" * 60


def format_digest(digest: Digest) -> str:
    """Return a multi-line string summary of *digest*."""
    lines: list[str] = []
    lines.append(SEP)
    lines.append(f"  Weekly Digest: {digest.owner}/{digest.repo}")
    lines.append(f"  Period: {digest.since.strftime('%Y-%m-%d %H:%M UTC')} → now")
    lines.append(SEP)

    # Commits
    lines.append(f"\n📦 Commits ({digest.commit_count})")
    for c in digest.commits[:5]:
        sha = c["sha"][:7]
        msg = c["commit"]["message"].splitlines()[0][:72]
        author = c["commit"]["author"]["name"]
        lines.append(f"  {sha}  {msg}  [{author}]")
    if digest.commit_count > 5:
        lines.append(f"  … and {digest.commit_count - 5} more")

    # Pull Requests
    lines.append(f"\n🔀 Pull Requests — {len(digest.merged_prs)} merged, {len(digest.open_prs)} open")
    for pr in (digest.merged_prs + digest.open_prs)[:5]:
        state = "merged" if pr.get("merged_at") else pr["state"]
        lines.append(f"  #{pr['number']} [{state}] {pr['title'][:70]}")

    # Issues
    lines.append(f"\n🐛 Issues — {len(digest.closed_issues)} closed, {len(digest.open_issues)} open")
    for issue in (digest.closed_issues + digest.open_issues)[:5]:
        lines.append(f"  #{issue['number']} [{issue['state']}] {issue['title'][:70]}")

    # Latest release
    lines.append("\n🚀 Latest Release")
    if digest.latest_release:
        rel = digest.latest_release
        lines.append(f"  {rel['tag_name']} — {rel['name']} ({rel['published_at'][:10]})")
    else:
        lines.append("  No releases found.")

    lines.append("\n" + SEP)
    return "\n".join(lines)
