"""Supplied file event sink; events stay in this product's .local/events."""
import json
import os
from pathlib import Path

def emit_event(event):
    # Stable keys give at-most-one persisted event per declared task attempt.
    # Classroom sink only; no email, Slack or external consumer is contacted.
    directory=Path(os.environ.get('CG_EVENT_DIR') or Path(__file__).resolve().parents[1]/'.local/events')
    directory.mkdir(parents=True,exist_ok=True)
    key=event['event_key']
    if not key or any(c not in 'abcdef0123456789' for c in key):
        raise ValueError('Event key must be a hexadecimal digest')
    path=directory/(key+'.json')
    payload=json.dumps(event,sort_keys=True)+'\n'
    try:
        with path.open('x') as f:
            f.write(payload)
    except FileExistsError:
        if json.loads(path.read_text())!=event:
            raise ValueError('Event identity reused for different content')
    return str(path)
