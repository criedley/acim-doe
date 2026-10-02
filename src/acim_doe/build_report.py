# build_report.py
import pandas as pd
from typing import Any, cast
from read_csv import read

def report(cycles: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    datasets = {
        "stab1": "data/stability1.csv",
        "stab2": "data/stability2.csv",
        "doe1": "data/doe1.csv",
        "doe2": "data/doe2.csv",
        "doe3": "data/doe3.csv",
}
    # dataframe to hold the report data
    df = pd.DataFrame(index=["stab1", "stab2", "doe1", "doe2", "doe3"])
    df["cycle_type"] = ["stability", "stability", "doe", "doe", "doe"]
    # dict to temporarily hold the dataframes for each dataset
    data = {name: read(path) for name, path in datasets.items()}
    # populate the report dataframe 'df' with metrics for each index/cycle
    for name, frame in data.items():
        df.loc[name, "avg_lsoc_md"] = frame["LSOC MD"].mean()
        df.loc[name, "start_time"] = frame["Timestamp"].iloc[0]
        df.loc[name, "end_time"] = frame["Timestamp"].iloc[-1]
        duration_minutes = (frame["Timestamp"].iloc[-1] - frame["Timestamp"].iloc[0]).total_seconds() / 60
        df.loc[name, "duration"] = duration_minutes
        # df.loc[name, "start_wh"] = frame["Watt-Hours"].iloc[0]
        # df.loc[name, "end_wh"] = frame["Watt-Hours"].iloc[-1]
        total_wh = float(frame["Watt-Hours"].iloc[-1] - frame["Watt-Hours"].iloc[0])
        df.loc[name, "total_kwh"] = total_wh / 1000
        harvest_weight = float(cast(Any, cycles.loc[name, "harvest weight"]))
        df.loc[name, "harvest_weight"] = harvest_weight
        # Calculate harvest rate (lbs per day)
        harvest_rate = harvest_weight / duration_minutes * 1440
        df.loc[name, "harvest_rate"] = harvest_rate
        energy = (total_wh / 1000)/harvest_weight * 100
        df.loc[name, "energy"] = energy  

    # build DOE summary 
    doe_rows = df.loc[df["cycle_type"] == "doe"]
    avg_harvest_rate = doe_rows["harvest_rate"].mean()
    avg_energy_use = doe_rows["energy"].mean()
    utilization = 0.42 if avg_harvest_rate > 50 else 0.14
    # watts
    standby_power = 5
    # kilowatt-hours
    standby_energy_use = (standby_power / 1000) * 24
    annual_enrgy_use = 365 * ((avg_energy_use / 100) * avg_harvest_rate * utilization + standby_energy_use * (1 - utilization))

    doe_summary = pd.DataFrame([{
        "avg_energy_use": avg_energy_use,
        # "avg_harvest_weight": doe_rows["harvest_weight"].mean(),
        "avg_harvest_rate": avg_harvest_rate,
        "doe_standard_2027": 22.99 - 0.27789 * avg_harvest_rate,
        "utilization": utilization,
        "standby_power": standby_power,
        "standby_energy_use": standby_energy_use,
        "annual_enrgy_use": annual_enrgy_use,

    }])

    return df, doe_summary