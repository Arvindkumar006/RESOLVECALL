import pytest
from resolvecall.core.models import Incident
from resolvecall.engine.planner import RecoveryPlanner


def test_planner_generates_correct_objective():
    inc = Incident(
        incident_id="INC-PHARMA-1",
        shipment_id="SHP-9988",
        failure_code="GATE_ACCESS_DENIED",
        failure_description="Missing security PIN at entrance",
        cargo_information="$50,000 vaccines",
        facility="BioStorage West",
        vendor="ColdChain Express",
        contact_name="Supervisor Jane",
        phone_number="+18005550100",
        recovery_deadline="11:30",
        authorization_info={"gate_code": "9921#", "po": "PO-123"},
        required_action="Provide gate code 9921# and schedule redelivery today before 11:30",
    )

    obj = RecoveryPlanner.create_call_objective(inc)
    assert obj.incident_id == "INC-PHARMA-1"
    assert obj.target_phone == "+18005550100"
    assert "ColdChain Express" in obj.prompt
    assert "Supervisor Jane" in obj.prompt
    assert "9921#" in obj.prompt
    assert "11:30" in obj.prompt
    assert "refuse" in obj.prompt.lower()
