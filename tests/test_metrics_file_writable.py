import os
import tempfile
import config.settings as settings


def test_metrics_dir_writable():
    """Fail if the directory where METRICS_FILE lives is not writable."""
    metrics_path = settings.METRICS_FILE
    parent = os.path.dirname(metrics_path) or '.'

    # Ensure parent exists
    os.makedirs(parent, exist_ok=True)

    # Attempt to create and remove a temp file in that directory
    try:
        fd, tmp = tempfile.mkstemp(dir=parent)
        os.close(fd)
        os.remove(tmp)
    except Exception as e:
        pytest_msg = (
            f"Metrics directory '{parent}' is not writable: {e}\n"
            "If you're running a frozen EXE, ensure the application writes to a user-writable path."
        )
        raise AssertionError(pytest_msg)
