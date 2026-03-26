import pandas as pd
import glob

files = glob.glob("dataset/monthly_processed_data/*.parquet")

dfs = []
for file in files:
    df = pd.read_parquet(file)
    
    # Münih filter
    df_münich = df[(df["final_destination_station"] == "München Hbf") | (df["station_name"] == "München Hbf")]

    if len(df_münich) == 0:
        continue

    # Max 100 random samples
    df_samples = df_münich.sample(n=100, random_state=42)
    dfs.append(df_samples)

final_df = pd.concat(dfs, ignore_index=True)
final_df.to_csv("mobility_dbt/seeds/historical_trips.csv", index=False)