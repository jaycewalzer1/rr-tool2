from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pandas as pd
import time
import numpy as np
import folium
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from collections import defaultdict

# Load your Excel file
file_path = "c:/Users/Max/OneDrive - Edgehill Real Estate Capital/Desktop/Data Monroe Deck.xlsx"
df = pd.read_excel(file_path)

# Initialize geocoder
geolocator = Nominatim(user_agent="geo_cluster", timeout=10)

def get_lat_lon(address):
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        time.sleep(1)
        return get_lat_lon(address)
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None, None
    return None, None

# Build full address
df["FULL_ADDRESS"] = df["SITE_ADDR"] + ", " + df["SITE_CITY"] + ", " + df["SITE_STATE"]
df[["Latitude", "Longitude"]] = df["FULL_ADDRESS"].apply(lambda x: pd.Series(get_lat_lon(x)))
df = df.dropna(subset=["Latitude", "Longitude"])

# Grid-Based Geographic Clustering
df["Lat_rounded"] = df["Latitude"].round(2)
df["Lon_rounded"] = df["Longitude"].round(2)
df["Cluster"] = df.groupby(["Lat_rounded", "Lon_rounded"]).ngroup()

# Save updated Excel
output_path = "c:/Users/Max/OneDrive - Edgehill Real Estate Capital/Desktop/clustered_properties_refined.xlsx"
df.to_excel(output_path, index=False)
print(f"Clustering completed! Saved as {output_path}")

# Map and Visuals
map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
property_map = folium.Map(location=map_center, zoom_start=13)

num_unique_clusters = len(set(df["Cluster"]))
cmap = cm.get_cmap("tab20", num_unique_clusters)
cluster_colors = {int(cluster): mcolors.rgb2hex(cmap(i)[:3]) for i, cluster in enumerate(set(df["Cluster"]))}

# Cluster summary
cluster_summary = defaultdict(lambda: {"count": 0, "total_val_transfer": 0})

if "VAL_TRANSFER" in df.columns:
    for _, row in df.iterrows():
        cluster_id = int(row["Cluster"])
        val_transfer = row["VAL_TRANSFER"]
        if not pd.isna(val_transfer):
            cluster_summary[cluster_id]["count"] += 1
            cluster_summary[cluster_id]["total_val_transfer"] += val_transfer

# Build table
table_html = """<h3>Cluster Summary</h3>
<table border="1" style="width:60%; text-align:center; font-family:Arial; border-collapse:collapse;">
<tr>
    <th>Cluster Color</th>
    <th>Total Pins</th>
    <th>Avg VAL_TRANSFER</th>
</tr>"""

for cluster_id, data in cluster_summary.items():
    avg_val = round(data["total_val_transfer"] / data["count"], 2) if data["count"] > 0 else 0
    table_html += f"""
    <tr>
        <td style='background-color:{cluster_colors.get(cluster_id, "#808080")};'></td>
        <td>{data["count"]}</td>
        <td>${avg_val:,.2f}</td>
    </tr>"""

table_html += "</table>"

# Plot markers with matching colors
for _, row in df.iterrows():
    cluster_id = int(row["Cluster"])
    color = cluster_colors.get(cluster_id, "#808080")
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=6,
        fill=True,
        fill_color=color,
        color=color,
        fill_opacity=0.8,
        popup=f"Address: {row['FULL_ADDRESS']}<br>Cluster: {cluster_id}"
    ).add_to(property_map)

# Save map with summary
map_output_path = "c:/Users/Max/OneDrive - Edgehill Real Estate Capital/Desktop/property_clusters_map_final.html"
html_map = property_map._repr_html_()
full_html = f"""
<!DOCTYPE html>
<html>
<head><title>Property Cluster Map</title></head>
<body>
    {table_html}
    {html_map}
</body>
</html>
"""

with open(map_output_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"Map created! Open the file: {map_output_path}")