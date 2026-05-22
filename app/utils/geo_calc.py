# File: app/utils/geo_calc.py
from geopy.distance import geodesic

def calculate_accurate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Silicon Valley Standard: Uses the WGS-84 ellipsoid model for highly accurate
    geodesic distance calculation, superior to the standard Haversine spherical model.
    Returns the straight-line distance in kilometers.
    """
    try:
        point_1 = (lat1, lon1)
        point_2 = (lat2, lon2)
        
        # Menghitung jarak dengan akurasi tinggi (mengembalikan nilai float KM)
        distance_km = geodesic(point_1, point_2).kilometers
        return round(distance_km, 2)
    except Exception as e:
        raise ValueError(f"Geolocation calculation failed: {str(e)}")