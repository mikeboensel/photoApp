from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import picEntry
from django.utils import timezone
from django.http import HttpResponse
from django.http import JsonResponse
import os.path
import os, sys
from PIL import Image

def index(request):
    pics = picEntry.objects.order_by('-upload_date')[:10]
    #imgLocation = '/static/picUpload/img/'
    #picDir = PROJECT_ROOT + imgLocation
    #img_list =os.listdir(picDir)
    img_list = []
    for p in pics:
        img_list.append({'thumbURL':p.thumbnail.url, 'fullSizeURL': p.pic.url, 'pk':p.pk})
    
    return render(request, 'pages/gallery.html', {'picList':img_list}) #todo work in dynamic determination of pics

size = 128, 128
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
#             p.upload_date = timezone.now() #now handled automatically in model 
            p.likes = 0
#             p.pic.save(file.name, file, save=False) #perhaps necessary, but think we can do a simpler assignment
#             p.pic = file
            
            if p.notDupe():
                p.save()
                addedFiles.append(p.thumbnail.url)
        
        #old Filestorage way
#         fs = FileSystemStorage()
#            filename = fs.save(myfile.name, myfile)

        #uploaded_file_url = fs.url(filename)
        #addedFiles = handle_uploaded_file(files)
        return JsonResponse({'success':True, 'addedFiles':addedFiles})
        #files = request.FILES.getlist('file_field')
        
    return JsonResponse({'success':False, 'msg':'Must be a POST'})

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

@login_required
def handleDeleteImg(request):
    #Would need check on ownership of file
    picPK = request.POST['pk']
    p = picEntry.objects.get(pk=picPK)
    if p.owner == request.user.id:
        p.delete()
    else:
        print("Invalid: Attempt by User {1} to delete photo {2} not belonging to them".format(request.user.id, picPK))
    return JsonResponse({'success':False, 'msg':'Received request'})
#     return JsonResponse({'success':False, 'msg':'Received request'}, status = 500) #non HTTP 200 response
