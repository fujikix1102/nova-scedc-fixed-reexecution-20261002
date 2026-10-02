import numpy as np
from third_party_reexecution.polarization_picker_v1 import pick_three_component, polarization_linearity


def test_linearity_increases_for_rank_one_signal():
    t = np.linspace(0, 1, 200)
    x = np.vstack([np.sin(20*t), 0.5*np.sin(20*t), -0.2*np.sin(20*t)])
    assert polarization_linearity(x) > 0.95


def test_picker_returns_candidate_and_fail_closed_claim():
    cft = np.zeros(100); cft[50] = 4.0
    t = np.linspace(0, 1, 100)
    x = np.vstack([np.sin(20*t), 0.5*np.sin(20*t), -0.2*np.sin(20*t)])
    result = pick_three_component(cft, x, 40.0)
    assert result["status"] == "CANDIDATE"
    assert result["selected"]["sample"] == 50
    assert result["formal_pass"] is False
