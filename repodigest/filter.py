"""Filtering utilities for repository activity data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FilterConfig:
    """Criteria used to narrow down digest items."""

    authors: List[str] = field(default_factory=list)          # include only these logins
    labels: List[str] = field(default_factory=list)           # include only these labels
    exclude_bots: bool = False                                 # drop logins ending with [bot]
    min_comments: int = 0                                      # minimum comment count
    title_contains: Optional[str] = None                      # substring match on title/message


def _is_bot(login: str) -> bool:
    return login.endswith("[bot]") or login.endswith("-bot")


def filter_commits(commits: list, cfg: FilterConfig) -> list:
    """Return commits that satisfy *cfg*."""
    result = []
    for c in commits:
        login = (c.get("author") or {}).get("login", "")
        if cfg.exclude_bots and _is_bot(login):
            continue
        if cfg.authors and login not in cfg.authors:
            continue
        message = (c.get("commit") or {}).get("message", "")
        if cfg.title_contains and cfg.title_contains.lower() not in message.lower():
            continue
        result.append(c)
    return result


def filter_prs(prs: list, cfg: FilterConfig) -> list:
    """Return pull requests that satisfy *cfg*."""
    result = []
    for pr in prs:
        login = (pr.get("user") or {}).get("login", "")
        if cfg.exclude_bots and _is_bot(login):
            continue
        if cfg.authors and login not in cfg.authors:
            continue
        pr_labels = [lbl["name"] for lbl in (pr.get("labels") or [])]
        if cfg.labels and not any(lbl in pr_labels for lbl in cfg.labels):
            continue
        if pr.get("comments", 0) < cfg.min_comments:
            continue
        if cfg.title_contains and cfg.title_contains.lower() not in pr.get("title", "").lower():
            continue
        result.append(pr)
    return result


def filter_issues(issues: list, cfg: FilterConfig) -> list:
    """Return issues that satisfy *cfg*."""
    result = []
    for issue in issues:
        login = (issue.get("user") or {}).get("login", "")
        if cfg.exclude_bots and _is_bot(login):
            continue
        if cfg.authors and login not in cfg.authors:
            continue
        issue_labels = [lbl["name"] for lbl in (issue.get("labels") or [])]
        if cfg.labels and not any(lbl in issue_labels for lbl in cfg.labels):
            continue
        if issue.get("comments", 0) < cfg.min_comments:
            continue
        if cfg.title_contains and cfg.title_contains.lower() not in issue.get("title", "").lower():
            continue
        result.append(issue)
    return result
