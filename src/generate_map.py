import folium
import pandas as pd
from branca.element import Template, MacroElement

# Load your CSV file
# Make sure to replace 'benches.csv' with your actual file path
df = pd.read_csv('benches.csv')
df = df.dropna(subset=["latitude", "longitude"])

# Create a base map centered on the average coordinates
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=14)

# Function to determine the color based on int_backrest
def get_color(backrest_value):
    if backrest_value == 1:
        return 'green'
    else:
        return 'yellow'

# Add points to the map
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=6,
        color='black',
        weight=0.5,
        fill=True,
        fill_color=get_color(row['int_backrest']),
        fill_opacity=0.8,
        popup=f"OSM ID: {int(row['id'])}"
    ).add_to(m)

tpl = """
{% macro script(this, kwargs) %}
    // Add a custom attribution entry (bottom-right)
    {{ this._parent.get_name() }}.attributionControl.addAttribution(
        '<h1>Où se poser à Toulouse, Castres et Albi</h1><a href="https://github.com/darkrecher/ou-se-poser/blob/main/README.md" target="_blank" rel="noopener">À propos de cette carte</a><br><br>'
    );
{% endmacro %}
"""
macro = MacroElement()
macro._template = Template(tpl)
m.add_child(macro)

# Save the map to an HTML file
m.save('ou_se_poser_a_toulouse.html')

print("Map saved as ou_se_poser_a_toulouse.html")
