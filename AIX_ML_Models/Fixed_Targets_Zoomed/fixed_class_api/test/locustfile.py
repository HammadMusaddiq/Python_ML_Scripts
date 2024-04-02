from locust import HttpUser, task

class BasicUser(HttpUser):

    @task
    def index(self):
        self.client.get("")

    @task
    def get_preds(self):
        self.client.post("get_predictions?img_url=https%3A%2F%2Fplay-lh.googleusercontent.com%2F1-hPxafOxdYpYZEOKzNIkSP43HXCNftVJVttoo4ucl7rsMASXW3Xr6GlXURCubE1tA%3Dw3840-h2160-rw")
