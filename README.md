# repodigest

A command-line utility that generates a concise weekly summary of GitHub repository activity via the API.

---

## Installation

```bash
pip install repodigest
```

Or install from source:

```bash
git clone https://github.com/yourusername/repodigest.git
cd repodigest
pip install -e .
```

---

## Usage

Set your GitHub personal access token:

```bash
export GITHUB_TOKEN=your_token_here
```

Generate a weekly summary for any public repository:

```bash
repodigest owner/repository
```

**Example:**

```bash
repodigest torvalds/linux
```

**Sample output:**

```
📦 torvalds/linux — Weekly Digest (2024-01-08 to 2024-01-15)
─────────────────────────────────────────────────────────────
🔀 Commits:    142
🐛 Issues:      23 opened / 18 closed
📬 Pull Requests: 31 opened / 27 merged
⭐ New Stars:   504
👥 Contributors:  38 active
```

**Options:**

| Flag | Description |
|------|-------------|
| `--weeks N` | Number of weeks to look back (default: 1) |
| `--format json` | Output results as JSON |
| `--repo-list file` | Digest multiple repos from a file |

---

## Requirements

- Python 3.8+
- GitHub Personal Access Token

---

## License

MIT © 2024 [Your Name](https://github.com/yourusername)