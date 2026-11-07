import subprocess, sys
from pathlib import Path
result=subprocess.check_output([sys.executable,'summarize.py'],cwd=Path(__file__).parent,text=True)
assert result == 'Portfolio summary\n6 holdings, total market value 12,011,626.50\n', result
print('summary oracle passed')
