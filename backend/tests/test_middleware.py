from uuid import UUID


def test_request_has_unique_id_header(client):
    response = client.get("/health")

    assert response.status_code == 200

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None

    # Validate that the value is a UUID.
    parsed_id = UUID(request_id)

    assert parsed_id.version == 4

def test_each_request_gets_different_id(client):
    first_response = client.get("/health")
    second_response = client.get("/health")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_id = first_response.headers.get("X-Request-ID")
    second_id = second_response.headers.get("X-Request-ID")

    assert first_id != second_id