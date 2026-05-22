# File: tests/test_main.py

def test_system_health_check(test_client):
    """
    Tests if the main entry point of the HOMS API is responding correctly
    and returning a 200 OK status.
    """
    response = test_client.get("/")
    
    # 1. Pastikan server merespons dengan sukses (Status 200)
    assert response.status_code == 200
    
    # 2. Ambil data JSON balasannya
    data = response.json()
    
    # 3. Pastikan tidak ada lagi nama MOST, harus murni HOMS!
    assert data["status"] == "online"
    assert "HOMS" in data["message"]