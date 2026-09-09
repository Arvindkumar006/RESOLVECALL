import pytest
from resolvecall.extraction.extractor import TranscriptExtractor


def test_extractor_parses_window_name_and_auth():
    sample_dialogue = [
        {"role": "agent", "text": "Hello, I am calling regarding shipment 9941. We need delivery before 11:30."},
        {"role": "dispatcher", "text": "This is Marcus from dispatch. I see the note about the gate code."},
        {"role": "agent", "text": "The gate access code is #4920*. Can the driver redeliver this morning?"},
        {"role": "dispatcher", "text": "Yes, I got the code. I can have the driver back between 10:45 and 11:15 AM."},
        {"role": "agent", "text": "Confirmed. Could you provide a confirmation code?"},
        {"role": "dispatcher", "text": "Your redelivery confirmation code is REDEL-9821."},
    ]

    call_data = {
        "status": "completed",
        "summary": "Driver re-routed to facility with gate code. Delivery confirmed for 10:45 to 11:15 AM.",
        "activities": sample_dialogue,
    }

    evidence = TranscriptExtractor.extract_evidence(call_data, sample_dialogue)
    assert evidence.resolution_status == "CONFIRMED"
    assert evidence.agreed_window_start == "10:45" or "10:45" in (evidence.agreed_window_start or "")
    assert evidence.agreed_window_end == "11:15 AM" or "11:15" in (evidence.agreed_window_end or "")
    assert evidence.representative_name == "Marcus"
    assert evidence.authorization_code == "REDEL-9821"
