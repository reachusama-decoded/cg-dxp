"""Supplied event-schema/hash primitives; contains no history correction/retry algorithm."""
import hashlib
import json
import math
import re
from datetime import date,datetime


def semantic_payload(event):
    # Attempt timestamp is operational metadata; the event contract lists statement fields.
    return {k:event[k] for k in ['event_id','product_id','metric','business_valid_from','business_valid_to','value','knowledge_time']}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_statement(event):
    # Validate shape/types only. Data Creators still implement identity/retry and interval behavior.
    date.fromisoformat(event['business_valid_from'])
    if event['business_valid_to'] is not None:
        date.fromisoformat(event['business_valid_to'])
        if event['business_valid_to']<=event['business_valid_from']:raise ValueError('Invalid business interval')
    datetime.fromisoformat(event['knowledge_time'].replace('Z','+00:00'))
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',event['knowledge_time']):raise ValueError('Expected fixed-width seconds-precision UTC Z fixture knowledge time')
    if event['metric']!='training_fee_bps':raise ValueError('Outside the synthetic metric contract')
    value=event['value']
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError('Expected finite numeric training value')
    return dict(event)
