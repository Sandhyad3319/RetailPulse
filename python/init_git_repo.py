"""
RetailPulse - Local Git Repository Initialization & Safe First Commit
Initializes a standard .git repository, enforces .gitignore exclusions,
and creates the initial commit.
"""

from pathlib import Path
from dulwich import porcelain
from dulwich.repo import Repo
from dulwich.ignore import IgnoreFilterManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def init_and_commit():
    print("=" * 65)
    print(" RetailPulse — Git Repository Initialization & Safety Audit")
    print("=" * 65)

    # 1. Initialize Repo
    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.exists():
        print(f"\n[1/4] Initializing new Git repository at:\n    {PROJECT_ROOT}")
        repo = porcelain.init(str(PROJECT_ROOT))
    else:
        print(f"\n[1/4] Existing Git repository detected at:\n    {PROJECT_ROOT}")
        repo = Repo(str(PROJECT_ROOT))

    # 2. Check Ignored Files
    print("\n[2/4] Auditing .gitignore exclusions...")
    ignore_manager = IgnoreFilterManager.from_repo(repo)

    files_to_add = []
    ignored_files = []
    large_files_detected = []

    for file_path in PROJECT_ROOT.rglob("*"):
        if not file_path.is_file():
            continue

        rel_path = file_path.relative_to(PROJECT_ROOT)
        rel_str = str(rel_path).replace("\\", "/")

        # Skip .git directory itself
        if rel_str.startswith(".git/"):
            continue

        # Check if ignored by .gitignore
        if list(ignore_manager.find_matching(rel_str)):
            ignored_files.append((rel_str, file_path.stat().st_size))
            continue

        # Safety: Check individual file size limit (50 MB warning, 100 MB block)
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            large_files_detected.append((rel_str, size_mb))
            continue

        files_to_add.append(rel_str)

    # Report Ignored Large Files
    print(f"    [OK] Protected {len(ignored_files)} excluded files from tracking:")
    for path, sz in ignored_files:
        print(f"         - {path} ({sz / (1024*1024):.2f} MB)")

    if large_files_detected:
        print("\n[ALERT] Blocked unignored files exceeding 50 MB:")
        for path, sz in large_files_detected:
            print(f"         - {path} ({sz:.2f} MB)")
        print("Please add these to .gitignore before committing.")
        return

    # 3. Stage Files
    print(f"\n[3/4] Staging {len(files_to_add)} safe project files...")
    porcelain.add(str(PROJECT_ROOT), paths=files_to_add)

    # 4. Create Initial Commit
    commit_msg = b"feat: RetailPulse - Retail Sales & Customer Intelligence Analytics Platform\n\nInitial repository commit including data processing pipelines, SQLite relational star schema, 15 business SQL queries, reports, Power BI data model/DAX specs, automated test suite, and interactive executive web dashboard."

    print("\n[4/4] Creating initial local commit...")
    commit_sha = porcelain.commit(
        str(PROJECT_ROOT),
        message=commit_msg,
        committer=b"RetailPulse Analyst <analyst@retailpulse.local>",
        author=b"RetailPulse Analyst <analyst@retailpulse.local>"
    )

    # Set default branch to main
    repo.refs[b"refs/heads/main"] = commit_sha
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/main")

    sha_str = commit_sha.decode("ascii") if isinstance(commit_sha, bytes) else str(commit_sha)

    print("\n" + "=" * 65)
    print(" [+] Git Repository Successfully Initialized & Committed!")
    print(f"     Branch:       main")
    print(f"     Commit SHA:   {sha_str[:10]}")
    print(f"     Files Staged: {len(files_to_add)}")
    print("=" * 65)


if __name__ == "__main__":
    init_and_commit()
