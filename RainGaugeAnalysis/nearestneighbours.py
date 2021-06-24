Skip to content
 
Search…
All gists
Back to GitHub
@masher92 
@ZaxR
ZaxR/nearest_neighbors.py
Last active 13 months ago • Report abuse
2
0
 Code
 Revisions 5
 Stars 2
<script src="https://gist.github.com/ZaxR/2f3614f49248bde1c0907d1b84a2bc9a.js"></script>
Find nearest neighbors by lat/long using Haversine distance with a BallTree
nearest_neighbors.py
"""
Example:
    # All locations; also locations FROM which we want to find nearest neighbors
    locations = pd.DataFrame({"LOCATION_NAME": ["Chicago, IL", "New York, NY", "San Fransisco, CA"],
                              "LATITUDE": [1, 2, 3],
                              "LONGITUDE": [1, 2, 3],
                              "ID": [1, 2, 3]})
    locations = locations.apply(lambda x: Location(location_name=x['LOCATION_NAME'],
                                                   latitude=x['LATITUDE'],
                                                   longitude=x['LONGITUDE'],
                                                   location_id=x['ID']),
                                axis=1).tolist()
    # Create locations FOR which we want to find nearest neighbors
    locs_of_int = ["Chicago, IL", "New York, NY"]
    locs_of_int = locations[locations['LOCATION_NAME'].isin(locs_of_int)]
    # Create map of each store to its closest neighbors
    nn_obj = NearestNeighborsMapper(locations=locs_of_int, neighbors=locations, closest_n=5)
    loc_map, nn_distances = nn_obj.create_closest_neighbors_map()
"""

from collections import OrderedDict
from collections.abc import Mapping

import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from sklearn.neighbors import BallTree

import config


def degrees_to_radians(row):
    lat = np.deg2rad(row[0])
    lon = np.deg2rad(row[1])

    return lat, lon


def radians_to_miles(rad):
    # Options here: https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    earth_radius = 6371.0087714150598
    mi_per_km = 0.62137119

    return rad * earth_radius * mi_per_km

def _parse_loc_desc(desc):
    # Implement your own location description parser here
    pass


def get_lat_long(desc, geolocator=Nominatim(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) "
                                                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                       "Chrome/68.0.3440.106 Safari/537.36")):
    # Note: You should cache results of this function, so it only needs to be run on new locations
    # Max of 1 API call per second per API policy: https://operations.osmfoundation.org/policies/nominatim/
    address = _parse_loc_desc(desc)
    time.sleep(1)
    location = geolocator.geocode(address, timeout=10)  # "Miami, FL"
    try:
        return location.latitude, location.longitude
    except AttributeError:
        return np.nan, np.nan
      

class Location(Mapping):
    __slots__ = ("location_name", "latitude", "longitude", "location_id")

    def __init__(self, location_name, latitude, longitude, location_id=None):
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.location_id = location_id

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __len__(self):
        return len(self.__slots__)

    def __iter__(self):
        return iter(self.__slots__)

    def items(self):
        for attribute in self.__slots__:
            if hasattr(self, attribute):
                yield attribute, getattr(self, attribute)

    def __repr__(self):
        return (f"{self.__class__.__name__}(location_name={self.location_name!r}, latitude={self.latitude!r}, "
                f"longitude={self.longitude!r}, location_id={self.location_id!r})")

    def __str__(self):
        return str(OrderedDict([(k, v) for k, v in self.items()]))


class NearestNeighborsMapper(object):
    """Map "locations" to their nearest "neighbors".
    Attributes:
        locations (list): Location objects for which we want nearest neighbors (from 'neighbors').
        neighbors (list): Location objects to be searched to find the nearest neighbors for 'locations'.
        closest_n (int): The number of nearest neighbors to find for each location. Default is 1.
        distance_metric (str): Distance metric, as used by sklearn's BallTree. Default is 'haversine'.
        distance_units (str): Units of the distance measurement. Default is 'miles'.
    """
    unit_dispatch = {'miles': radians_to_miles}

    def __init__(self, locations, neighbors, closest_n=1, distance_metric='haversine', distance_units='miles'):
        self.locations_df = self.create_df(locations)
        self.neighbors_df = self.create_df(neighbors)

        self.closest_n = closest_n
        self.distance_metric = distance_metric
        self.distance_units = distance_units

    @staticmethod
    def create_df(list_of_locations):
        df = pd.DataFrame(list_of_locations)
        rad_df = df[['latitude', 'longitude']].apply(degrees_to_radians, axis=1).apply(pd.Series)

        _combined_df = pd.concat([df, rad_df], axis=1)
        _combined_df.rename(columns={0: "rad_latitude", 1: "rad_longitude"}, inplace=True)

        return _combined_df

    # Haversine distance with a BallTree; requires Radians. Distances are output on Miles
    def create_closest_neighbors_map(self):
        tree = BallTree(self.neighbors_df[["rad_latitude", "rad_longitude"]],
                        leaf_size=2,
                        metric=self.distance_metric)

        # k adds 1 extra match to exclude a self match
        distances, indices = tree.query(self.locations_df[["rad_latitude", "rad_longitude"]], k=self.closest_n + 1)

        to_concat = []
        for i, m in enumerate(indices):
            loc = self.locations_df.iloc[i, :]['location_name']  # str of location of interest's name
            neighbors = self.neighbors_df.iloc[m, :]['location_name']  # pd.Series of n+1 nearest neighbors' names

            # Remove self matches (based on name) or last match if no self match
            if loc in neighbors.values:
                mask = (neighbors != loc)
                neighbors = neighbors[mask]
                miles = [distances[i][c] for c, b in enumerate(mask) if b]
                market_indices = [indices[i][c] for c, b in enumerate(mask) if b]
            else:
                neighbors = neighbors[:-1]
                miles = distances[i][:-1]
                market_indices = indices[i][:-1]

            # df for visibility into distances and index in market list
            for _, neighbor in enumerate(neighbors):
                to_concat.append([loc, neighbor, miles[_], market_indices[_]])

        df = pd.DataFrame(to_concat, columns=['location',
                                              "neighbor",
                                              f"distance ({self.distance_units})",
                                              "Index in list of neighbors"])
        df[f"distance ({self.distance_units})"] = (df[f"distance ({self.distance_units})"]
                                                   .apply(self.unit_dispatch[self.distance_units]))

        loc_map = df.groupby("location").agg({"neighbor": lambda x: list(x)})['neighbor'].to_dict()

        return loc_map, df
@masher92
 
Leave a comment
No file chosen
Attach files by dragging & dropping, selecting or pasting them.
© 2021 GitHub, Inc.
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
