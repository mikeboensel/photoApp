from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import picEntry, comment
from django.utils import timezone
from django.http import HttpResponse
from django.http import JsonResponse
import os.path
import os, sys
from PIL import Image
from struggla.users.models import User 
from _tkinter import create

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
            p.owner = request.user.id
            p.title = 'filler'
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
        if p.owner == request.user.id:
            p.delete() #TODO doesn't handle the actual photo files
            return createJSONMsg(True, 'Successfully delete pic with pk' + picPK, 200)
        else:
            return createJSONMsg(False, "Invalid: Attempt by User {0} to delete photo {1} not belonging to them".format(request.user.id, picPK), 403)

    except picEntry.DoesNotExist:
        return createJSONMsg(False, "Invalid call. Bad argument", 400)

def createJSONMsg(success, msg, status):
    if status != 200:
        print(msg) 
    return JsonResponse({'success':success, 'msg':msg}, status = status)

def index2(request):
    return HttpResponse('<h1> Getting: django.urls.exceptions.NoReverseMatch: Reverse for "gallery" with no arguments not found. 1 pattern(s) tried:</h1>')
    
    
@login_required
def handlePicCommentAction(request):
    msg = request.POST.get('msg', None)
    pk = request.POST.get('pk', None)

    if msg and pk:
        t = userIsAllowedToViewPic(request.user.id, pk)
        if t[0]:
            c = comment()
            c.associatePic = t[1]
            c.contents = msg #Possibly bad characters? Needs escaping?
            c.user = request.user.id
            c.save()
            return createJSONMsg(True, "Comment Added", 200)
        else:
            return createJSONMsg(False, "User does not have permission to comment on this picture", 403)
    else:
        return createJSONMsg(False, "Bad request data", 400)

#If pic public OR private and the user is the owner 
def userIsAllowedToViewPic(userId, picPK):
    try:
        p = picEntry.objects.get(pk=picPK)
        if p.public or p.owner == userId:
            return (True,p) #TODO better checks based on userId
    except picEntry.DoesNotExist:
        pass
    return (False, None)
    

@login_required
def handlePicPrivacyChange(request):
    pass

@login_required
def handlePicLike(request):
    pass