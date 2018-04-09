from django.urls import resolve, reverse
from django.test import TestCase
from .views import handleMultipleUpload
from picManager.views import handlePicLikeRetrieval, handlePicLikeUpdate, \
    handlePicPrivacyChange, handlePicDelete, index, getPicComments, \
    handlePicCommentAction, handlePicCommentEdit, handlePicCommentDelete
from picManager.models import picEntry, animal, comment, pictureLikes
from django.core.files.uploadedfile import SimpleUploadedFile
from struggla.users.models import User
import json
from datetime import timedelta, datetime, timezone

def universalTearDown():
    for p in picEntry.objects.all():
        p.pic.delete(save=False)
        p.thumbnail.delete(save=False)

class ViewResolutions(TestCase):
    
    def test_privacyChange_resolves_view(self):
        view = resolve('/gallery/handlePicPrivacyChange')
        self.assertEquals(view.func, handlePicPrivacyChange)

    def test_picLike_resolves_view(self):
        view = resolve('/gallery/handlePicLikeRetrieval')
        self.assertEquals(view.func, handlePicLikeRetrieval)
    
    def test_picLike_resolves_view2(self):
        view = resolve('/gallery/handlePicLikeUpdate')
        self.assertEquals(view.func, handlePicLikeUpdate)
        
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
        
    def test_comment_edit_resolves_view(self):
        view = resolve('/gallery/handlePicCommentEdit')
        self.assertEquals(view.func, handlePicCommentEdit)
    
    def test_comment_delete_resolves_view(self):
        view = resolve('/gallery/handlePicCommentDelete')
        self.assertEquals(view.func, handlePicCommentDelete)
    
    
    def create_pic(self):  # TODO WTF? What does this one even do?
        response = self.client.get('/media/ChessRobot.jpg')
        self.assertEquals(response.status_code, 200)        

"""For a lot of our testing this pretty simple baseline handles things"""
def baselineSetup():
    users = createUsers()
    pics = createPictures()
    picEntries = createPicEntries(users,pics)
    return {'users': users, "pics": pics, 'picEntries':picEntries}
# (users, pics, picEntries)
    
def createUsers():
    userA = User.objects.create_user(username='aGuy1', email='em@gmail.com', password='abc')
    userB = User.objects.create_user(username='aGuy2', email='em@gmail.com', password='abc')
    userC = User.objects.create_user(username='aGuy3', email='em@gmail.com', password='abc')
    return (userA, userB, userC)

def createPictures():
    pic_public = SimpleUploadedFile(name='_test_public.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
    pic_private = SimpleUploadedFile(name='_test_private.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
    return (pic_public, pic_private)

def createPicEntries(users, pics):
    public = picEntry.objects.create(pic=pics[0], owner=users[0], public=True, private=False)
    private = picEntry.objects.create(pic=pics[1], owner=users[0])
    return (public, private) 

def loginUser(instance, number):
    instance.client.login(username='aGuy' + str(number), password='abc')
    
class PictureVisibilityPermission(TestCase):
    @classmethod
    def setUpTestData(cls):
        baselineSetup()
             
    @classmethod
    def tearDownClass(cls):
        universalTearDown()
    
    def hit_invalid_page(self):
        return self.client.get('/gallery/notAGuy')
    
    def test_invalid_user_page_requested(self):
        response = self.hit_invalid_page()
        self.assertEqual(response.status_code, 404)
        
    def hit_valid_page(self):
        return self.client.get('/gallery/aGuy1') 

    def test_valid_user_page_requested_as_unauthenticated(self):
        response = self.hit_valid_page()
        # Had issues matching on _test_public.jpg. Tests seem to run in parallel meaning you get appended distinguishers (_test_publicSDCCXZ323.jpg) and non-deterministic test
        self.assertContains(response, '_test_public')
        self.assertNotContains(response, '_test_private')
        self.assertNotContains(response, 'dropzoneContainer')  # Can't upload pics

    def test_valid_user_page_requested_as_that_user(self):
        loginUser(self, 1)
        response = self.hit_valid_page()
        
        self.assertContains(response, '_test_public')
        self.assertContains(response, '_test_private')
        self.assertContains(response, 'dropzoneContainer')  # Can upload pics
        

    def test_valid_user_page_requested_as_different_user(self):
        loginUser(self, 2)
        response = self.hit_valid_page()
        
        self.assertContains(response, '_test_public')
        self.assertNotContains(response, '_test_private')
        self.assertNotContains(response, 'dropzoneContainer')  # Can't upload pics


class DeleteAction(TestCase):
    def setUp(self):
        users = createUsers()
        pics = createPictures()
                
        pEntry = picEntry.objects.create(pic=pics[0], owner=users[0], public=True, private=False)
        # TODO hacky. Necessary because we delete the PicEntry below. Don't trash files by default. Want to clean up for test cases
        self.pic = pEntry.pic
        self.pic_thumb = pEntry.thumbnail
        picEntry.objects.create(pic=pics[1], owner=users[0]) 
    
    # TODO super hacky. Refactor
    def safeDelete(self, file):
        try:
            file._get_file()
            file.delete()
        except (FileNotFoundError, ValueError):
            pass
    
    def tearDown(self):
        universalTearDown()
        self.safeDelete(self.pic)
        self.safeDelete(self.pic_thumb)    
        
    
    __url = '/gallery/handlePicDelete'
    
    def data_unchanged(self):
        self.assertEqual(len(picEntry.objects.all()), 2)  # Both pics should still exist
        # TODO better tests on it still being there

    def test_nonauthenticated_user_delete_req(self):
        response = self.client.post(DeleteAction.__url)
        self.assertEqual(response.status_code, 302)  # expect redirect to login

    def test_authenticated_user_nonowner_delete_req(self):
        loginUser(self, 2)
        data = {'pk':1}
        response = self.client.post(DeleteAction.__url, data=data)
        
        self.assertEqual(response.status_code, 403)  # Can't delete another user's pics
        self.data_unchanged()
        
    def test_authenticated_user_owner_delete_req(self):
        loginUser(self, 1)
        data = {'pk':1}
        responseJSON = self.client.post(DeleteAction.__url, data=data)

        self.assertEqual(responseJSON.status_code, 200)
        try:
            picEntry.objects.get(pk=1)
            self.fail("Deleted element still exists in DB!!!")
        except picEntry.DoesNotExist:
            pass
         
    def test_authenticated_user_bad_request(self):
        loginUser(self, 1)
        data = {'pk':88}  # Bad picEntry pk
        responseJSON = self.client.post(DeleteAction.__url, data=data)
        
        self.assertEqual(responseJSON.status_code, 400)
        self.data_unchanged()
        
    def test_authenticated_user_bad_request2(self):
        loginUser(self, 1)
        responseJSON = self.client.post(DeleteAction.__url)  # No picEntry arg
        
        self.assertEqual(responseJSON.status_code, 400)
        self.data_unchanged()

class CommentCreation(TestCase):
    def setUp(self):
        baselineSetup()
        
    def tearDown(self):
        universalTearDown()
    
    # TODO use reverse so that we aren't tightly coupled to URL mappings on refactoring (only viewTests are)
    # We want to test permissions. Only need to change logged in user and PK   
    def check_legit_comment_case(self, pk):
        msg = "New comment"
        data = {'pk':pk, 'msg':msg}
#         reverse(handlePicCommentAction, urlconf, args, kwargs, current_app)
        responseJSON = self.client.post('/gallery/handlePicCommentAction', data=data)
        
        self.assertEqual(responseJSON.status_code, 200)
        c = comment.objects.get(associatePic=pk)
        self.assertEqual(c.contents, msg)
    

    def test_user_comments_on_own_public_pic(self):
        loginUser(self, 1)
        self.check_legit_comment_case(1)
    
    def test_user_comments_on_own_private_pic(self):
        loginUser(self, 1)
        self.check_legit_comment_case(2)
    
    
    def test_userA_comments_on_userB_public_pic(self):
        loginUser(self, 2)
        self.check_legit_comment_case(1)

    def test_nonloggedin_user_comments(self):
        responseJSON = self.client.post('/gallery/handlePicCommentAction')
        self.assertEqual(responseJSON.status_code, 302)

    # expected client login prior. Permissions check
    def check_bad_comment_case(self, pk):
        responseJSON = self.client.post('/gallery/handlePicCommentAction', data={'msg':"w/e", "pk":pk})
        
        self.assertEqual(responseJSON.status_code, 403)  # forbidden
        self.assertEqual(0, len(comment.objects.all()))  # no comment created

    def test_userA_comments_on_userB_private_pic(self):
        loginUser(self, 2)
        self.check_bad_comment_case(2)
        
    def test_comment_on_nonexistent_pic(self):
        loginUser(self, 2)
        self.check_bad_comment_case(99)
        
class CommentRetrieval(TestCase):
    def setUp(self):
        tup = baselineSetup()
        
        # no comments on private pic, 2 on public
        comment.objects.create(associatePic=tup['picEntries'][0], user=tup['users'][1], contents="HideyHoo!")
        comment.objects.create(associatePic=tup['picEntries'][0], user=tup['users'][0], contents="Good to see you")
    
    def test_comment_delete_valid_user_comment_owner(self):
        loginUser(self, 2)
        self.delete_one_assert_rest_still_remain(1,2,1)
            
    def test_comment_delete_valid_user_pic_owner(self):
        loginUser(self, 1)
        self.delete_one_assert_rest_still_remain(1,2,1)

    def test_comment_delete_valid_user_comment_and_pic_owner(self):
        loginUser(self, 1)
        self.delete_one_assert_rest_still_remain(2,1,1)
    
    def delete_one_assert_rest_still_remain(self, expectedDeletedPK, expectedRemainingPK,  totalRemaining):
        response = self.client.post("/gallery/handlePicCommentDelete", data={"commentPK":expectedDeletedPK})
        self.assertEqual(response.status_code, 200)
        try:
            comment.objects.get(pk=expectedDeletedPK)
            self.fail("Comment {0} still exists after delete!".format(expectedDeletedPK))
        except comment.DoesNotExist:
            self.assertEqual(len(comment.objects.filter(pk=expectedRemainingPK)), 1) #ensure other comment still exists
            self.assertEqual(comment.objects.count(), totalRemaining) # and that its the only one
    
    def test_comment_delete_invalid_user(self):
        loginUser(self, 3)
        response = self.client.post("/gallery/handlePicCommentDelete", data={"commentPK":1})
        
        self.assertEqual(response.status_code, 403)
        self.check_data_unchanged()

    def test_comment_delete_non_loggedin_user(self):
        response = self.client.post("/gallery/handlePicCommentDelete", data={"commentPK":1})
        
        self.assertEqual(response.status_code, 302)
        self.check_data_unchanged()
    
    def test_comment_delete_non_existent_comment(self):
        loginUser(self, 1)
        response = self.client.post("/gallery/handlePicCommentDelete", data={"commentPK":99})

        self.assertEqual(response.status_code, 404)
    
    #TODO better tests
    def check_data_unchanged(self):
        self.assertEqual(comment.objects.count(), 2) #both items still exist
    
    ##############
    
    def test_comment_edit_valid_user_comment_owner(self):
        loginUser(self, 2)
        data = {"commentPK":1, "commentMsg":"New stuff"}
        response = self.client.post("/gallery/handlePicCommentEdit", data=data)
        
        self.assertEqual(response.status_code, 200)
        self.check_edit_occurred(data)
        
    def check_edit_occurred(self, data):
        try:
            c = comment.objects.get(pk=data["commentPK"])
            self.assertEqual(c.contents, data['commentMsg'])
            #expect an edit_date within the last minutes
            self.check_edit_time(c)
            
        except comment.DoesNotExist:
            self.fail("Cannot find editted comment")
            
        
    def check_edit_time(self, c):
        #TODO UTC ok? Brings up bigger question of determining where user is and what time to record
        #TODO hot mess. Come back to
#         margin = datetime.now() - timedelta(minutes=1) 
#         self.assertGreater(c.edit_date, margin)
        pass
    
#     def test_comment_edit_invalid_user_pic_owner(self):
#         self.client.login(username='aGuy', password='abc')
#         data = {"commentPK":2, "commentMsg":"New stuff"}
#         response = self.client.post("/gallery/handlePicCommentEdit", data=data)
#         
#         self.assertEqual(response.status_code, 403)
#         self.check_data_unchanged()
    
#     def test_comment_edit_valid_user_comment_and_pic_owner(self):
#         self.client.login(username='aGuy', password='abc')
#         data = {"commentPK":1, "commentMsg":"New stuff"}
#         response = self.client.post("/gallery/handlePicCommentEdit", data=data)
#         
#         self.assertEqual(response.status_code, 200)
#         
#         self.check_edit_occurred(data)
    
    def test_comment_edit_invalid_user(self): #neither comment owner or pic owner
        loginUser(self, 3)
        
        data = {"commentPK":1, "commentMsg":"New stuff"}
        response = self.client.post("/gallery/handlePicCommentEdit", data=data)
        
        self.assertEqual(response.status_code, 403)
        
        self.check_data_unchanged()
    
    def test_comment_edit_non_loggedin_user(self):
        data = {"commentPK":1, "commentMsg":"New stuff"}
        response = self.client.post("/gallery/handlePicCommentEdit", data=data)
        
        self.assertEqual(response.status_code, 302) #redirect
        
        self.check_data_unchanged()
    
#     def test_comment_edit_non_existent_comment(self):
#         self.client.login(username='aGuy3', password='abc')
#         
#         data = {"commentPK":99, "commentMsg":"New stuff"}
#         response = self.client.post("/gallery/handlePicCommentEdit", data=data)
#         
#         self.assertEqual(response.status_code, 400)
#         
#         self.check_data_unchanged()
    
    def tearDown(self):
        universalTearDown()

    def test_get_empty_comment_list(self):
        response = self.client.get('/gallery/getPicComments?pic=2')
        print(response)
        print(response.content)
        self.assertContains(response, '<ul id="commentList">')
        # Not bothering with proving its empty. Can always 
#         print(response.content)

    def test_get_2_comment_list(self):
        response = self.client.get('/gallery/getPicComments?pic=1')
        print(response.content)
        self.assertContains(response, 'HideyHoo!')
        self.assertContains(response, "Good to see you")
        
class LikeOperations(TestCase):
        
    def setUp(self):
        users = createUsers()
        
        # pk 1,2,3 respectively
        pic_public = SimpleUploadedFile(name='_test_public.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        pic_private = SimpleUploadedFile(name='_test_private.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')
        pic_public2 = SimpleUploadedFile(name='_test_public2.jpg', content=open('struggla\static\images\couple_in_car.jpg', 'rb').read(), content_type='image/jpeg')

        pic_entry_public = picEntry.objects.create(pic=pic_public, owner=users[0], public=True, private=False)
        picEntry.objects.create(pic=pic_private, owner=users[1])
        picEntry.objects.create(pic=pic_public2, owner=users[0], public=True, private=False)
         
        pictureLikes.objects.create(pic=pic_entry_public, user=users[1]) 

    def tearDown(self):
        universalTearDown()
    
    def test_getting_prior_like(self):
        loginUser(self, 2)
        responseJSON = self.client.get('/gallery/handlePicLikeRetrieval?pk=1')
        self.assertEqual(responseJSON.status_code, 200)
        j = json.loads(responseJSON.content)
        self.assertTrue(j['data']['isLiked'])

    def test_getting_no_prior_like(self):
        loginUser(self, 2)
        responseJSON = self.client.get('/gallery/handlePicLikeRetrieval?pk=2')
        self.assertEqual(responseJSON.status_code, 200)
        j = json.loads(responseJSON.content)
        self.assertFalse(j['data']['isLiked'])
        
    def test_permissions(self):
        loginUser(self, 1)
        responseJSON = self.client.get('/gallery/handlePicLikeRetrieval?pk=2')
        # Trying to get private photo details
        self.assertEqual(responseJSON.status_code, 403)
        
    def test_create_like(self):
        p = picEntry.objects.get(pk=3)
        self.assertEqual(p.likes, 0)
        
        loginUser(self, 2)
        
        responseJSON = self.client.post('/gallery/handlePicLikeUpdate', {'pk':3})
        self.assertEqual(responseJSON.status_code, 200)
        p = picEntry.objects.get(pk=3)
        self.assertEqual(p.likes, 1)   