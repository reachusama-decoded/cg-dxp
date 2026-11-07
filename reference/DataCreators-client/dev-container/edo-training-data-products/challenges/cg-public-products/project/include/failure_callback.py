"""AUTHOR phase 2: turn a real execution failure into a sanitized structured event.

Use runtime.event_sink.emit_event. Required fields/grain are in the project guide.
Do not confuse callback logging with the release gate or send external notifications.
"""
def on_failure(context):
    # AUTHOR: validate relevant context, define a stable event key and handle sink failure.
    raise NotImplementedError('Complete the failure callback')
