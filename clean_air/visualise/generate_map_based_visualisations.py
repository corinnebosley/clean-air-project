import webbrowser
import pandas as pd
from shapely.geometry import Point  # Shapely for converting lat/lon to geometry
import geopandas as gpd  # To create GeodataFrame
import folium
import os
import pathlib

from clean_air.visualise.assets import data
from clean_air.util import file_converter as fc
from clean_air.data import data_subset as ds

AURN_SITES = '/net/home/h05/clucas/CAF_Example_Data_Files/AURN_Observations/' \
             'AURN_Site_Information.csv'


def get_aurn__sites_site_map() -> map:
    """This function returns a site_map object with all the AURN sites plotted 
    on it.

    call display(site_map) to show this site_map in a Jupyter notebook
    There is also an html version generated for use at AURN.html '"""

    site_map = folium.Map(location=[50.72039, -1.88092], zoom_start=7)

    data_file = AURN_SITES
    df = pd.read_csv(data_file, skiprows=0, na_values=['no info', '.'])

    # Add geometry and convert to geopanda
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326",
                           geometry=gpd.points_from_xy(df.Longitude,
                                                       df.Latitude))

    # insert multiple markers, iterate through list
    # add a different color marker associated with type of volcano
    geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in gdf.geometry]

    i = 0
    for coordinates in geo_df_list:
        # assign a color marker for the type of AURN site
        if gdf.Type[i] == "URBAN_BACKGROUND":
            type_color = "green"
        elif gdf.Type[i] == "URBAN_TRAFFIC":
            type_color = "blue"
        elif gdf.Type[i] == "RURAL_BACKGROUND":
            type_color = "orange"
        else:
            type_color = "purple"

        # now place the markers with the popup labels and data
        site_map.add_child(folium.Marker(location=coordinates,
                                         popup=
                                         # "Year: " + str(gdf.Year[i]) + 
                                         # '<br>' +
                                         "Name: " + str(gdf.Name[i]) + '<br>' +
                                         "Type: " + str(gdf.Type[i]) + '<br>' + 
                                         "Coordinates: " + str(geo_df_list[i]),
                                         icon=folium.Icon(
                                             color="%s" % type_color)))
        # TODO: Remove trailing '+' from L.50 ("Type") if necessary.
        i = i + 1

    folium.LayerControl().add_to(site_map)

    site_map.save("assets/AURN.html")  # Save my completed site_map

    return site_map


def get_aircraft_track_map(aircraft_track_coords) -> map:
    """
    Create a standard base map, read and convert aircraft track files
    into lat/lon pairs, then plot these locations on the map and draw lines
    between them (and colour them by altitude?).
    """
    # Create base map
    m5 = folium.Map(location=[50.72039, -1.88092], zoom_start=8)

    # Extract lat-lon pairs from input file (after checking valid filetype):
    # TODO: What is a valid filetype here?
    filetype = os.path.splitext(aircraft_track_coords)[1]
    if filetype == '.html' or filetype == '.csv' or filetype == '.txt':
        pass
    elif filetype == '.nc':
        tmp_aircraft_df = fc.generate_dataframe(aircraft_track_coords)
        tmp_aircraft_track = []
        for row in tmp_aircraft_df.iterrows():
            lat = row[1]['Latitude']
            lon = row[1]['Longitude']
            tmp_aircraft_track.append([lat, lon])
        print(aircraft_track_coords)
    else:
        raise ValueError("Aircraft track filetype not recognised.  Please "
                         "ensure this is either......")
        # TODO: Finish writing this error message

    # Creating feature groups
    f1 = folium.FeatureGroup("Aircraft track 1")

    # Adding lines to the different feature groups
    line_1 = folium.vector_layers.PolyLine(tmp_aircraft_track,
                                           popup='<b>Path of Aircraft</b>',
                                           tooltip='Aircraft',
                                           color='blue', weight=5).add_to(f1)

    f1.add_to(m5)

    folium.LayerControl().add_to(m5)

    # Save my completed map
    # NOTE: I'm not hugely happy about this next bit, I am open to suggestions
    # about how to more easily specify this path:
    package_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(package_dir, 'assets/AircraftTrack.html')
    m5.save(save_path)

    return m5


# get_aurn__sites_map()
# get_aircraft_track_map(data.get_coords1())
# get_aircraft_track_map(AIRCRAFT_TRACK)

