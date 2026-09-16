"""Verify the portable artifact without registering an Explorer menu."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
exe = root / 'dist' / 'Simple File Converter.exe'
report_dir = root / 'build' / 'portable-check'
subprocess.run([str(exe), '--self-test', str(report_dir)], check=True, timeout=120)
report = json.loads((report_dir / 'report.json').read_text(encoding='utf-8'))
if not report.get('ok'):
    raise RuntimeError(report)
subprocess.run([str(exe), '--smoke-test'], check=True, timeout=60)
digest = hashlib.sha256(exe.read_bytes()).hexdigest()
(exe.parent / 'SHA256SUMS.txt').write_text(f'{digest}  {exe.name}\n', encoding='utf-8')
print(f'Portable verification passed: {len(report["checks"])} conversions')
