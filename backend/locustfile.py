"""
Locust Load Testing for Masal Fabrikası API
Run: locust -f locustfile.py --host=http://localhost:8000
"""
from locust import HttpUser, task, between
import random

class MasalFabrikasiUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts"""
        print("Starting user simulation...")
    
    @task(3)
    def get_root(self):
        """Test root endpoint"""
        self.client.get("/")
    
    @task(2)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")
    
    @task(1)
    def generate_story(self):
        """Test story generation (most important)"""
        themes = [
            "Bir ejderha ve prenses",
            "Uzayda macera",
            "Sihirli orman",
            "Cesur kahraman"
        ]
        
        response = self.client.post("/api/story/generate-story", json={
            "theme": random.choice(themes),
            "language": "tr",
            "story_type": "masal",
            "use_async": True,
            "save": False
        })
        
        if response.status_code == 200:
            data = response.json()
            if "job_id" in data:
                # Check job status
                self.client.get(f"/api/story/job/{data['job_id']}")
    
    @task(2)
    def get_stories(self):
        """Test fetching stories"""
        self.client.get("/api/story/stories?limit=10")
    
    @task(1)
    def get_characters(self):
        """Test fetching characters"""
        self.client.get("/api/character/characters")
    
    @task(1)
    def get_api_docs(self):
        """Test API documentation"""
        self.client.get("/docs")
