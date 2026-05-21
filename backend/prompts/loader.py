from pathlib import Path


def load_prompt(name: str) -> str:

    path = Path(
        f"backend/prompts/{name}.txt"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Prompt not found: {name}"
        )

    return path.read_text()
