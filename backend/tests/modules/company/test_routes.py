import unittest

from fastapi import FastAPI

from src.interfaces.api.v1 import router


class CompanyRouteTests(unittest.TestCase):
    def test_job_posting_is_nested_under_companies(self) -> None:
        app = FastAPI()
        app.include_router(router)
        operation = app.openapi()["paths"]["/v1/companies/job-postings"]["post"]

        self.assertEqual(operation["tags"], ["Companies"])

    def test_old_top_level_job_postings_route_is_not_registered(self) -> None:
        app = FastAPI()
        app.include_router(router)

        self.assertNotIn("/v1/job-postings", app.openapi()["paths"])
