from django.shortcuts import render, get_object_or_404

from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import picEntry, comment, pictureLikes
from django.utils import timezone
from django.http import HttpResponse
from django.http import JsonResponse
import os.path
import os, sys
from PIL import Image
from struggla.users.models import User 
from _tkinter import create
from django.http.response import Http404
from htmlmin.decorators import minified_response
from rest_framework.status import HTTP_400_BAD_REQUEST

def index(request, userName='admin'):
    
    userObj = get_object_or_404(User, username=userName)
   
    #determine permissions
    
    isPageOwner = False
    
    if request.user and request.user.is_authenticated:
        if request.user.id == userObj.pk: #logged in user requesting their own pictures. All pics available
            pics = picEntry.objects.order_by('-upload_date')[:10]
            isPageOwner = True
        else:
            #TODO finer granularity on permissions to sort out later
            pics = picEntry.objects.filter(public=True).order_by('-upload_date')[:10]
    else: #only display publicly viewable fields
        pics = picEntry.objects.filter(public=True).order_by('-upload_date')[:10]
            
    img_list = []
    for p in pics:
        img_list.append({'thumbURL':p.thumbnail.url, 'fullSizeURL': p.pic.url, 'pk':p.pk})
    #TODO pagination
    return render(request, 'pages/gallery.html', {'picList':img_list, 'isPageOwner': isPageOwner}) 

size = 300, 300
# Create your views here.
@login_required
def handleMultipleUpload(request):
    # currently have 2 different HTML approaches. Deciding between them. 
    if request.method == 'POST' and (request._files.getlist('files[]') or request._files.getlist('file')):
        files = request._files.getlist('files[]')
        if len(files) == 0:
            files = request._files.getlist('file')

        print(files)
        addedFiles = []
        for file in files:
            p = picEntry(pic = file)
            p.owner = request.user
            p.title = ''
#             p.pic.save(file.name, file, save=False) #perhaps necessary, but think we can do a simpler assignment
            
            if p.notDupe():
                p.save()
                addedFiles.append(p.thumbnail.url)
        
        return JsonResponse({'success':True, 'addedFiles':addedFiles})
        
    return JsonResponse({'success':False, 'msg':'Must be a POST'})

@login_required
def handlePicDelete(request):
    picPK = request.POST.get('pk', None)
    if not picPK:
        return createJSONMsg(False, "Invalid call. Missing argument", 400)
       
    try:
        p = picEntry.objects.get(pk=picPK)
        if p.owner == request.user:
            p.delete() #TODO doesn't handle the actual photo files
            return createJSONMsg(True, 'Successfully delete pic with pk' + picPK, 200)
        else:
            return createJSONMsg(False, "Invalid: Attempt by User {0} to delete photo {1} not belonging to them".format(request.user, picPK), 403)

    except picEntry.DoesNotExist:
        return createJSONMsg(False, "Invalid call. Bad argument", 400)

def createJSONMsg(success, msg, status, data ={}):
    if status != 200:
        print(msg) 
    return JsonResponse({'success':success, 'msg':msg, 'data':data}, status = status)

def index2(request):
    return HttpResponse('<h1> Getting: django.urls.exceptions.NoReverseMatch: Reverse for "gallery" with no arguments not found. 1 pattern(s) tried:</h1>')
    
    
@login_required
def handlePicCommentAction(request):
    msg = request.POST.get('msg', None)
    pk = request.POST.get('pk', None)

    if msg and pk:
        t = userIsAllowedToViewPic(request.user, pk)
        if t[0]:
            c = comment()
            c.associatePic = t[1]
            c.contents = msg #Possibly bad characters? Needs escaping?
            c.user = request.user
            c.save()
            return createJSONMsg(True, "Comment Added", 200)
        else:
            return createJSONMsg(False, "User does not have permission to comment on this picture", 403)
    else:
        return createJSONMsg(False, "Bad request data", 400)

"""If pic public OR private and the user is the owner
    Returns (Bool, User(Possibly None))
""" 
def userIsAllowedToViewPic(submittingUser, picPK):
    try:
        p = picEntry.objects.get(pk=picPK)
        if p.public or p.owner == submittingUser:
            return (True,p) 
    except picEntry.DoesNotExist:
        pass
    return (False, None)

def getPicComments(request):
    pk = request.GET.get('pic', None)
    if not pk:
        return Http404()
    
    comments = comment.objects.filter(associatePic=pk).order_by('-upload_date')
    return render(request, 'pages/commentList.html', {'comments':comments})

@login_required
def handlePicPrivacyChange(request):
    pass

"""Has the given user liked this photo?"""
@require_http_methods(["GET"])
@login_required
def handlePicLikeRetrieval(request):
    picPK = request.GET.get('pk', None)    
    tup = userIsAllowedToViewPic(request.user, picPK)
    
    if not tup[0]:
        return createJSONMsg(False, "Not authorized to comment on this pic (or pic does not exist)", 403)
    
    try:
        pictureLikes.objects.get(user = request.user, pic = tup[1])
        return createJSONMsg(True, 'User previously liked this pic', 200, {'isLiked': True})
    except pictureLikes.DoesNotExist:
        return createJSONMsg(True, 'User has NOT liked this pic', 200, {'isLiked': False})

"""Either creating a Like or destroying it (0-> +1) OR (+1 -> 0)"""
@require_http_methods(["POST"])
@login_required
def handlePicLikeUpdate(request):
    
    picPK = request.POST.get('pk')
    
    tup = userIsAllowedToViewPic(request.user, picPK)
    
    if not tup[0]:
        return createJSONMsg(False, "Not authorized to comment on this pic (or pic does not exist)", 403)
    
    try:
        #Existed, so +1 -> 0. Remove.
        likeObj = pictureLikes.objects.get(user = request.user, pic = tup[1])
        likeObj.delete()
        tup[1].likes = tup[1].likes-1
    except pictureLikes.DoesNotExist:
        #Create 0->1
        likeObj= pictureLikes(pic = tup[1], user = request.user)
        likeObj.save()
        tup[1].likes = tup[1].likes+1
        
    tup[1].save()
    
    return createJSONMsg(True, '', 200)