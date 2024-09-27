from locust import HttpUser, between, task


class MyAPIUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def index(self):
        self.client.get("http://34.47.86.69/app/create_user")
