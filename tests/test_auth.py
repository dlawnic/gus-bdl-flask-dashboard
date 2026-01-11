def test_register_and_login_flow(client):
    r = client.post("/register", data={"email": "a@b.com", "password": "password123", "password2": "password123"}, follow_redirects=True)
    assert r.status_code == 200
    assert "Konto utworzone" in r.get_data(as_text=True)

    r = client.post("/login", data={"email": "a@b.com", "password": "password123"}, follow_redirects=True)
    assert r.status_code == 200
    assert "Raport: rynek pracy" in r.get_data(as_text=True)

def test_protected_requires_login(client):
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code in (302, 401)
