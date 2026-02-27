from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models import Job, JobStatus
from app.core.database import SessionLocal

class JobRepository:
    def __init__(self, db_session: Session = None):
        self.db = db_session if db_session else SessionLocal()

    def create_job(self, job_data: Dict[str, Any]) -> Job:
        """Create a new job in the queue."""
        try:
            job = Job(
                id=UUID(job_data.get('id')) if job_data.get('id') else None,
                user_id=job_data['user_id'],
                story_id=job_data.get('story_id'),
                job_type=job_data['job_type'],
                status=JobStatus.QUEUED,
                input_data=job_data.get('input_data', {}),
                progress_percent=0
            )
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            return job
        except Exception as e:
            self.db.rollback()
            raise e

    def get_job_by_id(self, job_id: UUID) -> Optional[Job]:
        """Get a job by ID."""
        return self.db.query(Job).filter(Job.id == job_id).first()

    def get_active_jobs(self, user_id: UUID) -> List[Job]:
        """Get active jobs for a user."""
        return self.db.query(Job).filter(
            Job.user_id == user_id,
            Job.status.in_([JobStatus.QUEUED, JobStatus.RUNNING])
        ).all()

    def update_job_status(
        self, 
        job_id: UUID, 
        status: JobStatus, 
        result_data: Dict = None,
        error_message: str = None,
        percent: int = None,
        celery_task_id: str = None
    ) -> Optional[Job]:
        """Update job status and results."""
        job = self.get_job_by_id(job_id)
        if not job:
            return None
            
        job.status = status
        
        if result_data:
            job.result_data = result_data
            
        if error_message:
            job.error_message = error_message
            
        if percent is not None:
            job.progress_percent = percent
            
        if celery_task_id:
            job.celery_task_id = celery_task_id
            
        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.now()
            
        if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED]:
            job.completed_at = datetime.now()
            if status == JobStatus.SUCCEEDED:
                job.progress_percent = 100
        
        try:
            self.db.commit()
            self.db.refresh(job)
            return job
        except Exception as e:
            self.db.rollback()
            raise e
