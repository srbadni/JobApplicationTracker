from fastcrud import FastCRUD

from .models import JobPosting

crud_job_postings: FastCRUD = FastCRUD(JobPosting)