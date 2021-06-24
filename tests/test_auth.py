import os
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from flask import Flask

from amanuensis.db import User


def test_auth_circuit(app: Flask, make):
    """Test the user login/logout path."""
    username: str = f"user_{os.urandom(8).hex()}"
    ub: bytes = username.encode("utf8")
    user: User = make.user(username=username, password=username)

    with app.test_client() as client:
        # User should not be logged in
        response = client.get("/home/")
        assert response.status_code == 200
        assert ub not in response.data

        # The login page exists
        response = client.get("/auth/login/")
        assert response.status_code == 200
        assert ub not in response.data
        assert b"Username" in response.data
        assert b"Username" in response.data
        assert b"csrf_token" in response.data

        # Get the csrf token for logging in
        soup = BeautifulSoup(response.data, features="html.parser")
        csrf_token = soup.find(id="csrf_token")["value"]
        assert csrf_token

        # Log the user in
        response = client.post(
            "/auth/login/",
            data={"username": username, "password": username, "csrf_token": csrf_token},
        )
        assert 300 <= response.status_code <= 399
        assert urlsplit(response.location).path == "/home/"

        # Confirm that the user is logged in
        response = client.get("/home/")
        assert response.status_code == 200
        assert ub in response.data

        # Log the user out
        response = client.get("/auth/logout/")
        assert 300 <= response.status_code <= 399
        assert urlsplit(response.location).path == "/home/"

        # Confirm the user is logged out
        response = client.get("/home/")
        assert response.status_code == 200
        assert ub not in response.data
