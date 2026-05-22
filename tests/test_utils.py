# File: tests/test_utils.py
from app.utils.geo_calc import calculate_accurate_distance

def test_calculate_accurate_distance():
    """
    Tests the WGS-84 geodesic calculation engine to ensure dispatch 
    routing works accurately.
    """
    # Kordinat Monas, Jakarta
    lat1, lon1 = -6.1754, 106.8272
    
    # Kordinat Gedung Sate, Bandung
    lat2, lon2 = -6.9025, 107.6188
    
    # Eksekusi fungsi kalkulasi
    distance = calculate_accurate_distance(lat1, lon1, lat2, lon2)
    
    # Jarak Jakarta - Bandung garis lurus itu sekitar 119 - 120 KM.
    # Kita pastikan hasilnya masuk akal (di atas 100 KM dan di bawah 150 KM)
    assert distance > 100.0
    assert distance < 150.0
    
    # Pastikan tipe datanya Float, bukan String
    assert isinstance(distance, float)