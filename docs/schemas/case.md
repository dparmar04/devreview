# Case Schema

Each line in a dataset `.jsonl` file represents one code change (commit) evaluated by DevReview.

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique identifier for this case, e.g. `<repo>_<commit_sha[:10]>`. |
| `repo` | `string` | Name or identifier of the source git repository. |
| `commit_sha` | `string` | Full 40-character SHA-1 hex hash of the commit being reviewed. |
| `parent_sha` | `string` | Full 40-character SHA-1 hex hash of the commit's parent. |
| `label` | `"buggy" \| "clean"` | Ground truth label. `"buggy"` if this commit was found by SZZ to have introduced a bug later fixed. `"clean"` if it has no known fix, is older than the age cutoff, and touches code files. |
| `fix_sha` | `string \| null` | The SHA of the commit that fixed the bug introduced here. Always `null` for clean cases. |
| `buggy_locations` | `list[object]` | List of locations where the buggy code was planted. Empty list `[]` for clean cases. Each location object has: `introducing_sha` (string), `file` (string), `start_line` (int), `end_line` (int). |
| `diff` | `string` | The unified diff (`git diff parent_sha commit_sha`) representing the code change under review. Line count is bounded by `--max-diff-lines`. |

## Example: Buggy Case
```json
{
  "id": "my_project_a1b2c3d4e5",
  "repo": "my_project",
  "commit_sha": "a1b2c3d4e5f67890123456789012345678901234",
  "parent_sha": "0123456789abcdef0123456789abcdef01234567",
  "label": "buggy",
  "fix_sha": "f1e2d3c4b5a67890123456789012345678901234",
  "buggy_locations": [
    {
      "introducing_sha": "a1b2c3d4e5f67890123456789012345678901234",
      "file": "calculator.py",
      "start_line": 14,
      "end_line": 15
    }
  ],
  "diff": "--- a/calculator.py\n+++ b/calculator.py\n@@ -14,2 +14,2 @@\n- return a + b\n+ return a - b\n"
}
```

## Example: Clean Case
```json
{
  "id": "my_project_f9e8d7c6b5",
  "repo": "my_project",
  "commit_sha": "f9e8d7c6b5a43210987654321098765432109876",
  "parent_sha": "9876543210fedcba9876543210fedcba98765432",
  "label": "clean",
  "fix_sha": null,
  "buggy_locations": [],
  "diff": "--- a/logger.py\n+++ b/logger.py\n@@ -10,1 +10,3 @@\n+ def log_info(msg):\n+     print(msg)\n"
}
```

## Invariants & Validation Rules
1. `label` must be strictly `"buggy"` or `"clean"`.
2. When `label == "buggy"`:
   - `fix_sha` must be a valid commit SHA string.
   - `buggy_locations` must contain at least one location item.
3. When `label == "clean"`:
   - `fix_sha` must be `null`.
   - `buggy_locations` must be `[]`.
4. `diff` must not exceed `max_diff_lines` lines.

