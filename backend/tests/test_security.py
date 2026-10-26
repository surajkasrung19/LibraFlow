def test_security_headers_on_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    assert (
        response.headers["X-Content-Type-Options"]
        == "nosniff"
    )

    assert (
        response.headers["X-Frame-Options"]
        == "DENY"
    )

    assert (
        response.headers["Referrer-Policy"]
        == "no-referrer"
    )

def test_security_headers_on_reports_api(client):
    response = client.get("/api/v1/reports/overview")

    assert response.status_code == 200

    assert response.headers.get(
        "X-Content-Type-Options"
    ) == "nosniff"

    assert response.headers.get(
        "X-Frame-Options"
    ) == "DENY"

def test_api_response_disables_caching(client):
    response = client.get(
        "/api/v1/reports/overview"
    )

    assert response.status_code == 200

    assert response.headers.get(
            "Cache-Control"
        ) == "no-store"


def test_health_endpoint_has_no_api_cache_policy(client):
    response = client.get("/health")

    assert response.status_code == 200

    assert response.headers.get("Cache-Control") is None

    # General security headers should still be present
    assert response.headers.get(
        "X-COntent-Type-Options"
    ) == "nosniff"