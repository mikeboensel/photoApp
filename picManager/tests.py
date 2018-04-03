from django.urls import resolve, reverse
from django.test import TestCase
from .views import handleMultipleUpload
# Create your tests here.

class HomeTests(TestCase):
    # def test_home_view_status_code(self):
    #     url = reverse('home')
    #     response = self.client.get(url)
    #     self.assertEquals(response.status_code, 200)

    # def test_home_url_resolves_home_view(self):
    #     view = resolve('/')
    #     self.assertEquals(view.func, home)

    def test_pic_upload_resolves_home_view(self):
        view = resolve('/gallery/handleMultipleUpload')
        self.assertEquals(view.func, handleMultipleUpload)

    def create_pic(self):
        response = self.client.get('/media/ChessRobot.jpg')
        self.assertEquals(response.status_code, 200)        
