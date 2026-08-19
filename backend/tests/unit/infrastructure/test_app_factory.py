from src.infrastructure.app_factory import get_csrf_aware_swagger_ui_html


def test_swagger_ui_copies_csrf_cookie_to_header_for_unsafe_requests() -> None:
    response = get_csrf_aware_swagger_ui_html(openapi_url="/custom-openapi.json", title="API docs")
    html = response.body.decode("utf-8")

    assert "url: '/custom-openapi.json'" in html
    assert 'cookie.startsWith("csrf_token=")' in html
    assert 'request.headers["X-CSRF-Token"]' in html
    assert '["POST", "PUT", "PATCH", "DELETE"]' in html
    assert 'request.credentials = "same-origin"' in html
