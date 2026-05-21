import subprocess

def run_code(code: str):
    with open('temp.py', 'w') as f:
        f.write(code)
    result = subprocess.run(
        ['python3', 'temp.py'],
        capture_output=True,
        text=True
    )
    return result.stdout
