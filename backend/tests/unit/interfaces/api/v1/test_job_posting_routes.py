from src.interfaces.main import app


def test_job_posting_route_uses_current_top_level_path() -> None:
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/job_postings"]["post"]

    assert operation["tags"] == ["Job Postings"]
    assert "/api/v1/companies/{company_id}/job-postings" not in schema["paths"]
