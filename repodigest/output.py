"""Output helpers for repodigest — write digest to stdout or a file."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from repodigest.formatter import format_digest
from repodigest.digest import Digest


SUPPORTED_FORMATS = ("text", "markdown", "json")


def _digest_to_json(digest: Digest) -> str:
    """Serialize a Digest to a JSON string."""
    import json
    from datetime import datetime

    def _pr_to_dict(pr: dict) -> dict:
        return {
            "number": pr.get("number"),
            "title": pr.get("title", ""),
            "user": (pr.get("user") or {}).get("login", ""),
        }

    data = {
        "repo": digest.repo,
        "since": digest.since.isoformat(),
        "commit_count": digest.commit_count,
        "open_prs": digest.open_prs,
        "merged_prs": digest.merged_prs,
        "open_issues": digest.open_issues,
        "closed_issues": digest.closed_issues,
        "new_releases": digest.new_releases,
        "top_contributors": digest.top_contributors,
    }
    return json.dumps(data, indent=2, default=str)


def render(digest: Digest, fmt: str = "text") -> str:
    """Render *digest* in the requested *fmt*.

    Parameters
    ----------
    digest:
        Populated :class:`~repodigest.digest.Digest` instance.
    fmt:
        One of ``"text"``, ``"markdown"``, or ``"json"``.

    Returns
    -------
    str
        The rendered output as a string.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format {fmt!r}. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    if fmt == "json":
        return _digest_to_json(digest)

    # Both "text" and "markdown" delegate to the existing formatter;
    # the formatter already produces Markdown-friendly output.
    return format_digest(digest)


def write_output(
    digest: Digest,
    fmt: str = "text",
    output_path: Optional[str] = None,
) -> None:
    """Render *digest* and write to *output_path* or stdout.

    Parameters
    ----------
    digest:
        Populated :class:`~repodigest.digest.Digest` instance.
    fmt:
        Rendering format (``"text"``, ``"markdown"``, ``"json"``).
    output_path:
        File path to write to.  If *None* the result is printed to stdout.
    """
    content = render(digest, fmt=fmt)

    if output_path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
    else:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
