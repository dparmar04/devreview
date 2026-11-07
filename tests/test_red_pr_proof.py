import os


def test_red_pr_cannot_be_merged():
    """Throwaway probe for T-005 proof (b), second attempt.

    Passes locally (CI is unset) and fails on GitHub Actions (CI=true), because a test
    that failed locally could never be pushed: the pre-push hook runs `make verify`.
    """
    assert os.environ.get("CI") != "true", "deliberate red check for T-005 proof"
