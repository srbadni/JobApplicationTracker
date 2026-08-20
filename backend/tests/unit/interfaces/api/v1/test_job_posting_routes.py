from src.interfaces.main import app


def test_job_posting_route_is_nested_under_company() -> None:
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/companies/{company_id}/job-postings"]["post"]

    assert operation["tags"] == ["Job Postings"]
    assert "/api/v1/employers/job_postings" not in schema["paths"]
