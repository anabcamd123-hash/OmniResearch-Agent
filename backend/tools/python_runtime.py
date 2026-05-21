import subprocess
import tempfile
import os


class PythonRuntime:

    def execute(self, code: str):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".py",
            mode="w",
            encoding="utf-8"
        ) as f:

            f.write(code)

            path = f.name

        try:

            result = subprocess.run(
                ["python3", path],
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        finally:

            os.remove(path)
