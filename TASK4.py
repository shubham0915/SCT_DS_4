import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import numpy as np

# Initialize dictionaries to aggregate data across chunks
weather_counts = {}
road_counts = {"Traffic_Signal": 0, "Crossing": 0, "Junction": 0}
hourly_counts = np.zeros(24)
day_counts = {}

# Process dataset in chunks
chunk_size = 100000  # Adjust based on your system's memory
for chunk in pd.read_csv("dataset4.csv", chunksize=chunk_size):
    # Convert Start_Time to datetime
    chunk["Start_Time"] = pd.to_datetime(chunk["Start_Time"], errors="coerce")

    # Aggregate weather conditions
    wc = chunk["Weather_Condition"].value_counts(dropna=False)
    for w, c in wc.items():
        weather_counts[w] = weather_counts.get(w, 0) + c

    # Aggregate road conditions
    for col in ["Traffic_Signal", "Crossing", "Junction"]:
        road_counts[col] += chunk[col].sum()

    # Aggregate time patterns
    chunk["Hour"] = chunk["Start_Time"].dt.hour
    hourly_counts += chunk["Hour"].value_counts().reindex(range(24), fill_value=0).values
    chunk["Day_of_Week"] = chunk["Start_Time"].dt.day_name()
    dc = chunk["Day_of_Week"].value_counts()
    for d, c in dc.items():
        day_counts[d] = day_counts.get(d, 0) + c

# Convert aggregated data to series/dataframes
weather_series = pd.Series(weather_counts)
road_series = pd.Series(road_counts)
day_series = pd.Series(day_counts)

# Basic information (from first chunk)
first_chunk = next(pd.read_csv("dataset4.csv", chunksize=chunk_size))
print("Dataset Shape:", (7728394, len(first_chunk.columns)))
print("\nData Types:\n", first_chunk.dtypes)
print("\nFirst 5 Rows:\n", first_chunk.head())

# Summary statistics (approximate, based on first chunk)
print("\nSummary Statistics:\n", first_chunk.describe())

# Check for missing values (approximate, based on first chunk)
print("\nMissing Values (Sample):\n", first_chunk.isnull().sum())

# EDA Results
print("\nWeather Condition Distribution:")
print(weather_series.sort_values(ascending=False).head(10))

print("\nAccidents with Traffic_Signal:", road_series["Traffic_Signal"])
print("Accidents with Crossing:", road_series["Crossing"])
print("Accidents with Junction:", road_series["Junction"])

print("\nAccident Distribution by Hour:")
print(pd.Series(hourly_counts, index=range(24)))

print("\nAccident Distribution by Day of Week:")
print(day_series.sort_values(ascending=False))

# Visualizations
# 1. Heatmap for Accident Hotspots (using all data, processed in chunks)
all_data = pd.concat([chunk for chunk in pd.read_csv("dataset4.csv", chunksize=chunk_size)])
map_center = [all_data["Start_Lat"].mean(), all_data["Start_Lng"].mean()]
m = folium.Map(location=map_center, zoom_start=4)
heat_data = [[row["Start_Lat"], row["Start_Lng"]] for index, row in
             all_data.dropna(subset=["Start_Lat", "Start_Lng"]).iterrows()]
HeatMap(heat_data).add_to(m)
folium.LayerControl().add_to(m)
m.save("accident_hotspots.html")
print("Open 'accident_hotspots.html' in a web browser to view the heatmap.")

# 2. Bar Chart for Weather Conditions
plt.figure(figsize=(10, 6))
weather_top5 = weather_series.sort_values(ascending=False).head(5)
sns.barplot(x=weather_top5.index, y=weather_top5.values, palette="Blues_d")
plt.title("Top 5 Weather Conditions in Accidents")
plt.xlabel("Weather Condition")
plt.ylabel("Number of Accidents")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("weather_conditions.png")
plt.close()

# 3. Bar Chart for Road Conditions
plt.figure(figsize=(10, 6))
sns.barplot(x=road_series.index, y=road_series.values, palette="Greens_d")
plt.title("Accidents by Road Conditions")
plt.xlabel("Road Condition")
plt.ylabel("Number of Accidents")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("road_conditions.png")
plt.close()

# 4. Line Chart for Hourly Trends
plt.figure(figsize=(10, 6))
plt.plot(range(24), hourly_counts, marker="o", color="orange")
plt.title("Accident Distribution by Hour of Day")
plt.xlabel("Hour of Day")
plt.ylabel("Number of Accidents")
plt.grid(True)
plt.tight_layout()
plt.savefig("hourly_trends.png")
plt.close()