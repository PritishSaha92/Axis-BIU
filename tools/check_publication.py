"""Fail if Git-tracked/public files contain common internship publication risks."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "_private", "__pycache__", ".venv", "venv"}
PATTERN_ALLOWLIST = {Path(".gitignore"), Path("tools/check_publication.py")}
BLOCKED_SUFFIXES = {
    ".bak",
    ".csv",
    ".docx",
    ".gif",
    ".jpeg",
    ".jpg",
    ".key" + "tab",
    ".orc",
    ".p12",
    ".parquet",
    ".pem",
    ".pfx",
    ".pdf",
    ".png",
    ".pptx",
    ".webp",
    ".xls",
    ".xlsx",
    ".zip",
}
BINARY_ALLOWLIST = {Path("docs/assets/collector-ring.png")}
ALLOWED_PATTERN_MATCHES = {
    "domain name requiring review": {"excalidraw.com"},
}
PATTERNS = {
    "possible employee identifier": re.compile(r"\b[A-Z]{2}\d{8}\b"),
    "possible customer/account identifier": re.compile(r"\b\d{9}\b"),
    "domain name requiring review": re.compile(
        r"\b(?:[a-z0-9-]+\.)+(?:com|net|org|in|corp|internal|local)\b",
        re.IGNORECASE,
    ),
    "internal-looking schema": re.compile(
        r'''["'][a-z][a-z0-9_]*(?:_dev|_prod|_uat|_ods|_dm)["']''',
        re.IGNORECASE,
    ),
    "authentication material": re.compile(
        "key" + "tab|" + "kinit|" + r"spark\.principal", re.IGNORECASE
    ),
    "absolute distributed-filesystem path": re.compile(r"\b(?:hdfs|viewfs)://", re.IGNORECASE),
    "private network address": re.compile(
        r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
    ),
    "internal compute namespace": re.compile(
        r"\b[a-z0-9_]+\.(?:DEV|PROD|UAT)\.[a-z0-9_.]+\b", re.IGNORECASE
    ),
    "internal-review marking": re.compile(r"\binternal review\b", re.IGNORECASE),
}


def candidate_files() -> Iterable[Path]:
    try:
        output = subprocess.check_output(
            [
                "git",
                "-c",
                "safe.directory={}".format(ROOT.as_posix()),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
        )
        tracked = [item for item in output.decode("utf-8").split("\0") if item]
        if tracked:
            return [ROOT / item for item in tracked]
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        pass

    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not (set(path.relative_to(ROOT).parts) & SKIP_PARTS)
    ]


def notebook_findings(path: Path) -> List[str]:
    if path.suffix.lower() != ".ipynb":
        return []
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return ["notebook is not valid UTF-8 JSON"]

    findings = []
    for index, cell in enumerate(notebook.get("cells", []), start=1):
        if cell.get("execution_count") is not None:
            findings.append("cell {} has an execution count".format(index))
        if cell.get("outputs"):
            findings.append("cell {} has saved output".format(index))
    return findings


def main() -> int:
    findings = []
    for path in sorted(candidate_files()):
        relative = path.relative_to(ROOT)
        if set(relative.parts) & SKIP_PARTS:
            continue
        if (
            path.suffix.lower() in BLOCKED_SUFFIXES
            and relative not in BINARY_ALLOWLIST
        ):
            findings.append("{}: blocked file type".format(relative))
            continue

        for message in notebook_findings(path):
            findings.append("{}: {}".format(relative, message))

        if relative in PATTERN_ALLOWLIST:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for label, pattern in PATTERNS.items():
            allowed = ALLOWED_PATTERN_MATCHES.get(label, set())
            if any(match.group(0).lower() not in allowed for match in pattern.finditer(text)):
                findings.append("{}: {}".format(relative, label))

    if findings:
        print("Publication check failed:")
        for finding in findings:
            print(" -", finding)
        return 1

    print("Publication check passed for public/tracked files.")
    print("Manual authorization and confidentiality review are still required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
