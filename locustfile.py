from locust import HttpUser, task, between

class EnterpriseAIHRMUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # We assume public routes or mock auth for benchmarking
        # Normally we'd login here and save token/session
        pass

    @task(3)
    def view_recruitment_portal(self):
        self.client.get("/recruitment/public_portal")

    @task(1)
    def ai_employee_risk(self):
        # Without auth this might return 401, but we just want to load the endpoint
        self.client.get("/ai/employee/1/risk")

    @task(1)
    def ai_employee_explain(self):
        self.client.get("/ai/employee/1/explain")

    @task(1)
    def ai_employee_recommendations(self):
        self.client.get("/ai/employee/1/recommendations")

    @task(2)
    def submit_exam_mock(self):
        # Mocks an exam submission. We expect 404/redirect for nonexistent candidate,
        # but the request routing itself is tested.
        self.client.post("/recruitment/submit_test/999", data={
            "exam_id": 1,
            "q_1": "A"
        })
