#!/usr/bin/env bash
set -euo pipefail
mkdir lab
cd lab
git init -q -b main
git config user.name 'Training Learner'
git config user.email 'learner@example.invalid'
printf '# Holdings contract\n\nOwner: Training team\nGrain: one row per fund and instrument\nCurrency: USD\nDelivery: daily\n' > contract.md
git add contract.md
git commit -qm 'Record holdings contract'
git switch -qc clarify-delivery
sed -i 's/Delivery: daily/Delivery: daily before 09:00 UTC/' contract.md
git commit -qam 'Clarify delivery deadline'
git switch -q main
git switch -qc clarify-owner
sed -i 's/Owner: Training team/Owner: Analytics team/' contract.md
git commit -qam 'Assign training owner'
git switch -q main
git merge -q --no-ff clarify-delivery -m 'Integrate delivery clarification'
git merge -q --no-ff clarify-owner -m 'Integrate ownership'
sed -i 's/Owner: Analytics team/Owner: Training team/' contract.md
git commit -qam 'Record training ownership baseline'
git switch -qc upstream-owner
sed -i 's/Owner: Training team/Owner: Operations team/' contract.md
git commit -qam 'Propose operations owner'
git switch -q main
sed -i 's/Owner: Training team/Owner: Analytics team/' contract.md
git commit -qam 'Confirm analytics owner'
if git merge upstream-owner -m 'Resolve owner' 2>/dev/null; then
  echo 'Expected merge conflict was absent' >&2; exit 1
fi
python3 - <<'INNER'
from pathlib import Path
p=Path('contract.md');lines=p.read_text().splitlines()
start=next(i for i,line in enumerate(lines) if line.startswith('<<<<<<<'))
end=next(i for i,line in enumerate(lines) if line.startswith('>>>>>>>'))
lines[start:end+1]=['Owner: Analytics team','Escalation: Training support']
p.write_text(chr(10).join(lines)+chr(10))
INNER
git add contract.md
git commit -qm 'Resolve ownership and retain escalation'
printf '
Accidental text
' >> contract.md
git restore contract.md
test -z "$(git status --porcelain)"
git log --oneline --graph --all
