import pandas as pd
import numpy as np

def build_hospital_kpi_report(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(columns=["metric", "value"])
    occupancy_rate = np.round((dataframe["occupied_beds"] / dataframe["total_beds"]).mean() * 100, 2)
    return pd.DataFrame([
        {"metric": "average_occupancy_rate", "value": occupancy_rate},
        {"metric": "total_hospitals", "value": int(dataframe["hospital_name"].nunique())},
    ])
