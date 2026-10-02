import hashlib
import json
from pathlib import Path

import numpy as np
from obspy import read, read_events
from obspy.signal.trigger import classic_sta_lta, trigger_onset

BASE = Path("data/empirical_validation/scedc_seismic_20261002")
OUT = Path("output/nova_scedc_fixed_runner_phase_parity_20261002_v1.json")
CASES = {
    "14608980": (BASE / "event_14608980", ["BOM", "BOR", "DRE"]),
    "14609500": (BASE / "event_14609500", ["BOM", "BOR", "DRE"]),
    "14609660": (BASE / "event_ci14609660_eventwindow", ["BOM", "BOR", "CTC", "DRE"]),
    "14610172": (BASE / "event_14610172", ["BOM", "BOR", "CTC", "DRE"]),
}

CONTRACT = {
    "component": "BHZ",
    "detrend": "linear",
    "taper_fraction": 0.02,
    "filter": {"type": "bandpass", "freqmin_hz": 0.5, "freqmax_hz": 8.0, "corners": 3, "zerophase": True},
    "sta_seconds": 0.5,
    "lta_seconds": 5.0,
    "trigger_on": 3.0,
    "trigger_off": 1.5,
    "candidate_window_seconds": 20.0,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    records = []
    for event_id, (root, stations) in CASES.items():
        phase_file = root.parent / (f"event_{event_id}" if event_id != "14609660" else "event_ci14609660") / f"scedc_phases_{event_id}.xml"
        catalog = read_events(str(phase_file))
        picks = {
            p.waveform_id.station_code: p.time
            for p in catalog[0].picks
            if p.waveform_id and p.waveform_id.station_code in stations and p.phase_hint == "P"
        }
        for station in stations:
            wave_path = root / f"CI_{station}_BHZ.mseed"
            trace = read(str(wave_path))[0]
            trace.detrend("linear")
            trace.taper(CONTRACT["taper_fraction"])
            filt = CONTRACT["filter"]
            trace.filter(
                "bandpass",
                freqmin=filt["freqmin_hz"],
                freqmax=filt["freqmax_hz"],
                corners=filt["corners"],
                zerophase=filt["zerophase"],
            )
            pick = picks.get(station)
            if pick is None:
                records.append({"event": event_id, "station": station, "status": "MISSING_OFFICIAL_PICK", "input_sha256": sha256(wave_path)})
                continue
            rel = float(pick - trace.stats.starttime)
            center = int(rel * trace.stats.sampling_rate)
            half = int(CONTRACT["candidate_window_seconds"] * trace.stats.sampling_rate)
            lo, hi = max(0, center - half), min(len(trace.data), center + half)
            data = trace.data.astype(float)
            cft = classic_sta_lta(data, int(CONTRACT["sta_seconds"] * trace.stats.sampling_rate), int(CONTRACT["lta_seconds"] * trace.stats.sampling_rate))
            triggers = trigger_onset(cft, CONTRACT["trigger_on"], CONTRACT["trigger_off"])
            candidates = [{"offset_s": float(i / trace.stats.sampling_rate), "end_offset_s": float(j / trace.stats.sampling_rate), "abs_error_s": float(abs(i / trace.stats.sampling_rate - rel))} for i, j in triggers if lo <= i < hi]
            records.append({
                "event": event_id, "station": station, "status": "COMPLETED", "input_sha256": sha256(wave_path),
                "npts": int(trace.stats.npts), "sampling_rate_hz": float(trace.stats.sampling_rate),
                "start": str(trace.stats.starttime), "end": str(trace.stats.endtime),
                "official_pick": str(pick), "official_pick_offset_s": rel,
                "trigger_candidates": candidates,
                "nearest_abs_error_s": min((x["abs_error_s"] for x in candidates), default=None),
            })
    result = {"runner": "run_scedc_fixed_phase_parity_v1.py", "contract": CONTRACT, "records": records, "all_inputs_hashed": all("input_sha256" in r for r in records), "formal_pass": False}
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT} ({len(records)} station-event records)")


if __name__ == "__main__":
    main()
