from django.db import models
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import hashlib
from struggla.users.models import User as AuthUser


class picEntry(models.Model):
    # 	https://docs.python.org/3/library/hashlib.html
    # 	https://www.pythoncentral.io/hashing-files-with-python/
    def _createHash(self):
        if not self.sha256:
            hasher = hashlib.sha256()
            BLOCKSIZE = 65536

            afile = self.pic._get_file()
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
                    
            self.sha256 = hasher.hexdigest()            

    title = models.CharField(max_length=30)
    pic = models.ImageField()
    thumbnail = models.ImageField(default=None, blank=True, null=True)
    likes = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(
        AuthUser,
        on_delete=models.CASCADE,
    )
    
    #Everything starts off private. 
    public = models.BooleanField(default=False)
    private = models.BooleanField(default=True)
    #More granular permissions to come     
    # commentThreadIndex =
    #TODO currently using PK. Might want to generate something like this
# 	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True) #uuid generation

    upload_date = models.DateTimeField(auto_now_add=True)
# 	https://stackoverflow.com/questions/16853815/how-to-generate-hash-for-django-model
    sha256 = models.CharField(max_length=64)  # , default=_createHash)

    def notDupe(self):
        if not self.sha256:
            self._createHash()
        
        p = picEntry.objects.all().filter(sha256=self.sha256)
        return len(p) == 0
    
    def __str__(self):
        return 'sha256={0}\npic={1}'.format(self.sha256, self.pic)

    def save(self, *args, **kwargs):
        self._createHash()
        if not self.make_thumbnail():
            # set to a default thumbnail
            raise Exception('Could not create thumbnail for {0} - is the file type valid?'.format(self.pic.name))
        super(picEntry, self).save(*args, **kwargs)

    size = (300, 300)

# https://stackoverflow.com/questions/23922289/django-pil-save-thumbnail-version-right-when-image-is-uploaded?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    def make_thumbnail(self):

        with Image.open(self.pic._get_file()) as image:
            image.thumbnail(picEntry.size, Image.ANTIALIAS)
    
            thumb_name, thumb_extension = os.path.splitext(self.pic.name)
            thumb_extension = thumb_extension.lower()
    
            thumb_filename = thumb_name + '_thumb' + thumb_extension
    
            if thumb_extension in ['.jpg', '.jpeg']:
                FTYPE = 'JPEG'
            elif thumb_extension == '.gif':
                FTYPE = 'GIF'
            elif thumb_extension == '.png':
                FTYPE = 'PNG'
            else:
                return False  # Unrecognized file type
    
            # Save thumbnail to in-memory file as StringIO
            temp_thumb = BytesIO()
            image.save(temp_thumb, FTYPE)
            temp_thumb.seek(0)
    
            # set save=False, otherwise it will run in an infinite loop
            self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
            temp_thumb.close()
    
            return True

class comment(models.Model):
    associatePic = models.ForeignKey(
        picEntry,
        on_delete=models.CASCADE,
    )
    
    user = models.ForeignKey(
        AuthUser,
        on_delete=models.CASCADE,
    ) 
    
    contents = models.CharField(max_length=500)
    upload_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(default=None, blank=True, null=True)


class animal(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    number_we_have = models.PositiveIntegerField(default=0)
