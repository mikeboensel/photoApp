from django.urls import resolve, reverse
from django.test import TestCase
from .views import handleMultipleUpload
from picManager.views import *
from picManager.models import picEntry, animal
from django.core.files.uploadedfile import SimpleUploadedFile

class ViewTests(TestCase):
    
    def test_privacyChange_resolves_view(self):
        view = resolve('/gallery/handlePicPrivacyChange')
        self.assertEquals(view.func, handlePicPrivacyChange)

    def test_picLike_resolves_view(self):
        view = resolve('/gallery/handlePicLike')
        self.assertEquals(view.func, handlePicLike)
        
    def test_picDelete_resolves_view(self):
        view = resolve('/gallery/handlePicDelete')
        self.assertEquals(view.func, handlePicDelete)

    def test_username_resolves_view(self):
        view = resolve('/gallery/aUserName')
        self.assertEquals(view.func, index)
    
    def test_picUpload_resolves_view(self):
        view = resolve('/gallery/handleMultipleUpload')
        self.assertEquals(view.func, handleMultipleUpload)    
    
    def create_pic(self):  # TODO WTF? What does this one even do?
        response = self.client.get('/media/ChessRobot.jpg')
        self.assertEquals(response.status_code, 200)        


class VisibilityPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='aGuy', email='em@gmail.com', password='abc')
        User.objects.create_user(username='aGuy2', email='em@gmail.com', password='abc')
        pic_public = SimpleUploadedFile(name='_test_public.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        pic_private = SimpleUploadedFile(name='_test_private.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        
        picEntry.objects.create(pic=pic_public, owner=1, public=True, private=False)
        picEntry.objects.create(pic=pic_private, owner=1)
             
    @classmethod
    def tearDownClass(cls):
        for p in picEntry.objects.all():
            p.pic.delete(save=False)
            p.thumbnail.delete(save=False)
    
    def hit_invalid_page(self):
        return self.client.get('/gallery/notAGuy')
    
    def test_invalid_user_page_requested(self):
        response = self.hit_invalid_page()
        self.assertEqual(response.status_code, 404)
        
    def hit_valid_page(self):
        return self.client.get('/gallery/aGuy') 

    def test_valid_user_page_requested_as_unauthenticated(self):
        response = self.hit_valid_page()
        # Had issues matching on _test_public.jpg. Tests seem to run in parallel meaning you get appended distinguishers (_test_publicSDCCXZ323.jpg) and non-deterministic test
        self.assertContains(response, '_test_public')
        self.assertNotContains(response, '_test_private')
        self.assertNotContains(response, 'dropzoneContainer')  # Can't upload pics

    def test_valid_user_page_requested_as_that_user(self):
        self.client.login(username='aGuy', password='abc')
        response = self.hit_valid_page()
        
        self.assertContains(response, '_test_public')
        self.assertContains(response, '_test_private')
        self.assertContains(response, 'dropzoneContainer')  # Can upload pics
        

    def test_valid_user_page_requested_as_different_user(self):
        self.client.login(username='aGuy2', password='abc')
        response = self.hit_valid_page()
        
        self.assertContains(response, '_test_public')
        self.assertNotContains(response, '_test_private')
        self.assertNotContains(response, 'dropzoneContainer')  # Can't upload pics


class DeleteTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='aGuy', email='em@gmail.com', password='abc')
        User.objects.create_user(username='aGuy2', email='em@gmail.com', password='abc')
        pic_public = SimpleUploadedFile(name='_test_public.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        pic_private = SimpleUploadedFile(name='_test_private.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        
        picEntry.objects.create(pic=pic_public, owner=1, public=True, private=False)
        picEntry.objects.create(pic=pic_private, owner=1)
        
    def tearDown(self):
        for p in picEntry.objects.all():
            p.pic.delete(save=False)
            p.thumbnail.delete(save=False) 
    
    __url = '/gallery/handlePicDelete'
    
    def data_unchanged(self):
        self.assertEqual(len(picEntry.objects.all()), 2)  # Both pics should still exist
        # TODO better tests on it still being there

    
    def test_nonauthenticated_user_delete_req(self):
        response = self.client.post(DeleteTests.__url)
        self.assertEqual(response.status_code, 302)  # expect redirect to login

    def test_authenticated_user_nonowner_delete_req(self):
        self.client.login(username='aGuy2', password='abc')
        data = {'pk':1}
        response = self.client.post(DeleteTests.__url, data=data)
        
        self.assertEqual(response.status_code, 403)  # Can't delete another user's pics
        self.data_unchanged()
        
    def test_authenticated_user_owner_delete_req(self):
        self.client.login(username='aGuy', password='abc')
        data = {'pk':1}
        responseJSON = self.client.post(DeleteTests.__url, data=data)
        self.assertEqual(responseJSON.status_code, 200)
        #TODO assert item deleted
        try:
            picEntry.objects.get(pk=1)
            self.fail("Deleted element still exists in DB!!!")
        except picEntry.DoesNotExist:
            pass

            
    def test_authenticated_user_bad_request(self):
        self.client.login(username='aGuy', password='abc')
        data = {'pk':88} #Bad picEntry pk
        responseJSON = self.client.post(DeleteTests.__url, data=data)
        
        self.assertEqual(responseJSON.status_code, 400)
        self.data_unchanged()
        
    def test_authenticated_user_bad_request2(self):
        self.client.login(username='aGuy', password='abc')
        responseJSON = self.client.post(DeleteTests.__url) #No picEntry arg
        
        self.assertEqual(responseJSON.status_code, 400)
        self.data_unchanged()

class AnimalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        animal.objects.create(name="Gorilla", type="Mammal", number_we_have=1)

    def setup(self):
        animal.objects.create(name="Gorilla", type="Mammal", number_we_have=1)
    
#     def test(self):
#         print(animal.objects.get(name="Gorilla").type)


    
