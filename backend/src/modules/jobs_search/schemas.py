from ..job_posting.schemas import JobPostingBase


class JobSearchRead(JobPostingBase):
    company_title: str
    job_category_title: str
    province_title: str
    salary_range_title: str
    city_title: str