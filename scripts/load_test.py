from locust import HttpUser, task, between, events, LoadTestShape
import random
import string

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class InterviewUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        """Register and login before starting tasks"""
        self.email = f"loadtest_{random_string()}@example.com"
        self.password = "StrongPassword123!"
        
        # Register
        self.client.post("/api/v1/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": "Load Test User"
        })
        
        # Login
        response = self.client.post("/api/v1/auth/login", data={
            "username": self.email,
            "password": self.password
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            self.token = None

    @task(3)
    def create_and_fetch_interviews(self):
        """Simulate creating an interview and fetching the dashboard"""
        if not self.token: return
        
        # Create
        res = self.client.post("/api/v1/interviews/sessions", json={
            "title": "Load Test Interview",
            "job_role": "SWE",
            "difficulty": "medium"
        })
        
        # Fetch dashboard
        self.client.get("/api/v1/interviews/sessions")

    @task(1)
    def fetch_user_profile(self):
        """Simulate fetching user profile data"""
        if not self.token: return
        self.client.get("/api/v1/users/me")

class StagedLoadShape(LoadTestShape):
    """
    A custom load shape that stages the traffic to test breaking points.
    Stage 1: 10 concurrent users
    Stage 2: 25 concurrent users
    Stage 3: 50 concurrent users
    Stage 4: 100 concurrent users
    """
    
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},     # Stage 1: Hold 10 users for 1 min
        {"duration": 120, "users": 25, "spawn_rate": 5},    # Stage 2: Hold 25 users for 1 min
        {"duration": 180, "users": 50, "spawn_rate": 10},   # Stage 3: Hold 50 users for 1 min
        {"duration": 240, "users": 100, "spawn_rate": 20},  # Stage 4: Hold 100 users for 1 min
    ]

    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
                
        return None # Stops the test

# To run: locust -f scripts/load_test.py --host=http://localhost:8000
