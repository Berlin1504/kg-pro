import subprocess
result = subprocess.run(
    ["python", "-c", "from backend.main import app; routes = [(r.path, r.methods) for r in app.routes]; [print(p, m) for p, m in routes if 'fee' in p.lower() or 'template' in p.lower()]"],
    capture_output=True, text=True, cwd=r"d:\Apps\classify"
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr[-500:] if result.stderr else "")
