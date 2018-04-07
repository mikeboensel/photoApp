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

    def test_commmentAction_resolves_view(self):
        view = resolve('/gallery/handlePicCommentAction')
        self.assertEquals(view.func, handlePicCommentAction)   
        
    def test_get_comment_resolves_view(self):
        view = resolve('/gallery/getPicComments?pic=1')
        self.assertEquals(view.func, getPicComments)   
    
    def create_pic(self):  # TODO WTF? What does this one even do?
        response = self.client.get('/media/ChessRobot.jpg')
        self.assertEquals(response.status_code, 200)        


class VisibilityPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        userA = User.objects.create_user(username='aGuy', email='em@gmail.com', password='abc')
        User.objects.create_user(username='aGuy2', email='em@gmail.com', password='abc')
        pic_public = SimpleUploadedFile(name='_test_public.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        pic_private = SimpleUploadedFile(name='_test_private.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        
        picEntry.objects.create(pic=pic_public, owner=userA, public=True, private=False)
        picEntry.objects.create(pic=pic_private, owner=userA)
             
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
        userA = User.objects.create_user(username='aGuy', email='em@gmail.com', password='abc')
        userB = User.objects.create_user(username='aGuy2', email='em@gmail.com', password='abc')
        pic_public = SimpleUploadedFile(name='_test_public.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        pic_private = SimpleUploadedFile(name='_test_private.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        
        picEntry.objects.create(pic=pic_public, owner=userA, public=True, private=False)
        picEntry.objects.create(pic=pic_private, owner=userA) 
        
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

#Comment tests (don't want to repeat setup)

    # We want to test permissions. Only need to change logged in user and PK   
    def check_legit_comment_case(self, pk):
        msg = "New comment"
        data = {'pk':pk, 'msg':msg}
        responseJSON = self.client.post('/gallery/handlePicCommentAction', data=data)
        
        self.assertEqual(responseJSON.status_code, 200)
        c = comment.objects.get(associatePic = pk)
        self.assertEqual(c.contents, msg)
    

    def test_user_comments_on_own_public_pic(self):
        self.client.login(username='aGuy', password='abc')
        self.check_legit_comment_case(1)
    
    def test_user_comments_on_own_private_pic(self):
        self.client.login(username='aGuy', password='abc')
        self.check_legit_comment_case(2)
    
    
    def test_userA_comments_on_userB_public_pic(self):
        self.client.login(username='aGuy2', password='abc')
        self.check_legit_comment_case(1)

    def test_nonloggedin_user_comments(self):
        responseJSON = self.client.post('/gallery/handlePicCommentAction')
        self.assertEqual(responseJSON.status_code, 302)

    #expected client login prior. Permissions check
    def check_bad_comment_case(self, pk):
        responseJSON = self.client.post('/gallery/handlePicCommentAction', data = {'msg':"w/e", "pk":pk})
        
        self.assertEqual(responseJSON.status_code, 403) #forbidden
        self.assertEqual(0, len(comment.objects.all())) #no comment created

    def test_userA_comments_on_userB_private_pic(self):
        self.client.login(username='aGuy2', password='abc')
        self.check_bad_comment_case(2)
        
    def test_comment_on_nonexistent_pic(self):
        self.client.login(username='aGuy2', password='abc')
        self.check_bad_comment_case(99)
        

class CommentRetrieval(TestCase):
    def setUp(self):
        userA = User.objects.create_user(username='aGuy', email='em@gmail.com', password='abc')
        userB = User.objects.create_user(username='aGuy2', email='em@gmail.com', password='abc')
        pic_public = SimpleUploadedFile(name='_test_public.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        pic_private = SimpleUploadedFile(name='_test_private.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        
        pic_entry_public = picEntry.objects.create(pic=pic_public, owner=userA, public=True, private=False)
        picEntry.objects.create(pic=pic_private, owner=userA) 
        
        #no comments on private pic, 2 on public
        comment.objects.create(associatePic=pic_entry_public, user=userB, contents="HideyHoo!")
        comment.objects.create(associatePic=pic_entry_public, user=userA, contents="Good to see you")
    
    def tearDown(self):
        for p in picEntry.objects.all():
            p.pic.delete(save=False)
            p.thumbnail.delete(save=False) 

    def test_get_empty_comment_list(self):
        response = self.client.get('/gallery/getPicComments?pic=2')
        print(response)
        print(response.content)
        self.assertContains(response,'<ul id="commentList">')
        #Not bothering with proving its empty. Can always 
#         print(response.content)

    def test_get_2_comment_list(self):
        response = self.client.get('/gallery/getPicComments?pic=1')
        print(response.content)
        self.assertContains(response,'HideyHoo!')
        self.assertContains(response, "Good to see you")
        

        
class AnimalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        animal.objects.create(name="Gorilla", type="Mammal", number_we_have=1)

    def setup(self):
        animal.objects.create(name="Gorilla", type="Mammal", number_we_have=1)
    
#     def test(self):
#         print(animal.objects.get(name="Gorilla").type)


    
