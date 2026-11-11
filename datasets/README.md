# Datasets

Golden evaluation datasets generated from real-world open-source repositories.

## `datasets/requests.jsonl`

- **Source Repository:** [psf/requests](https://github.com/psf/requests)
- **Repository URL:** `https://github.com/psf/requests.git`
- **Source Commit Hash:** `3c7baaa05ab4aa49cc819ce3a819d260de19c157`
- **License:** Apache License 2.0
- **Language:** Python
- **Build Parameters:**
  - `--max-diff-lines`: 400
  - `--min-age-days`: 90

### Case Counts
| Category | Count | Percentage |
|---|---|---|
| **Buggy Cases** | 538 | 25.3% |
| **Clean Cases** | 1,591 | 74.7% |
| **Total Cases** | 2,129 | 100.0% |
| **Skipped Cases** (diff > 400 lines) | 92 | — |

### Notes on Ground Truth & Label Noise
- A case is marked **buggy** if SZZ identified it as introducing lines that were later modified or removed by a bug fix commit.
- A case is marked **clean** if it modified source code files, is at least 90 days older than the newest commit in history, and was never associated with a subsequent fix commit.
- "Clean" indicates "no known fix in git history", not a mathematical guarantee of zero bugs.

