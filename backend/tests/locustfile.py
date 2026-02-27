"""
Load Testing with Locust
"""
from locust import HttpUser, task, between, tag
import random


class MasalFabrikasiUser(HttpUser):
    """Simulated user behavior for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts"""
        # Login (if auth is enabled)
        # response = self.client.post("/api/auth/login", json={
        #     "email": "test@example.com",
        #     "password": "test123"
        # })
        # self.token = response.json().get("access_token")
        pass
    
    @task(3)
    @tag("read")
    def view_health(self):
        """View health check"""
        self.client.get("/health")
    
    @task(5)
    @tag("read")
    def list_stories(self):
        """List stories"""
        user_id = "00000000-0000-0000-0000-000000000000"
        self.client.get(f"/api/stories?user_id={user_id}")
    
    @task(2)
    @tag("read")
    def get_story_detail(self):
        """Get a specific story"""
        # This assumes you have stories in the database
        story_id = "some-story-id"  # Replace with actual ID
        self.client.get(f"/api/stories/{story_id}")
    
    @task(1)
    @tag("write", "heavy")
    def generate_story(self):
        """Generate a new story (expensive operation)"""
        themes = [
            "Uzayda kaybolmuş bir kedi",
            "Sihirli orman",
            "Deniz altında macera",
            "Zamanda yolculuk",
            "Robot arkadaş"
        ]
        
        self.client.post("/api/generate-story", json={
            "theme": random.choice(themes),
            "language": "tr",
            "story_type": "masal",
            "use_async": True
        })
    
    @task(2)
    @tag("read")
    def get_analytics(self):
        """Get analytics dashboard"""
        user_id = "00000000-0000-0000-0000-000000000000"
        self.client.get(f"/api/value/analytics/dashboard/{user_id}")
    
    @task(1)
    @tag("read")
    def get_achievements(self):
        """Get achievements"""
        user_id = "00000000-0000-0000-0000-000000000000"
        self.client.get(f"/api/value/achievements/user/{user_id}")


class AdminUser(HttpUser):
    """Admin user behavior"""
    
    wait_time = between(2, 5)
    
    @task
    @tag("admin")
    def view_detailed_health(self):
        """View detailed health check"""
        self.client.get("/health/detailed")
    
    @task
    @tag("admin")
    def check_metrics(self):
        """Check Prometheus metrics"""
        self.client.get("/metrics")


# Run with:
# locust -f locustfile.py --host=http://localhost:8000
#
# Options:
# --users 100     # Number of concurrent users
# --spawn-rate 10 # Users spawned per second
# --run-time 5m   # Test duration
# --headless      # No Web UI
#
# Example:
# locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 2m
