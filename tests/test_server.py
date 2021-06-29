from flask import Flask


def test_app_testing(app: Flask):
    """Confirm that the test config loads correctly."""
    assert app.testing


def test_client(app: Flask):
    """Test that the test client works."""
    with app.test_client() as client:
        response = client.get("/home/")
        assert b"Amanuensis" in response.data
