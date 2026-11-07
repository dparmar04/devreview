import os


def test_ci_only_failure():
    """Deliberate failure used once in T-004 to prove that CI turns red.

    Passes locally (CI is unset) and fails on GitHub Actions (CI=true). The local
    pre-push hook runs `make verify`, so a test that failed locally could never be
    pushed without --no-verify, which is forbidden. Making the failure CI-only
    keeps the local gate honest and still proves the server-side gate.
    """
    assert os.environ.get("CI") != "true", "deliberate CI-only failure for T-004"
