import os
import os.path as op

from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
from config import UPLOAD_FOLDER, IMG_UPLOAD_FOLDER, IMG_UPLOAD_URL
import uuid

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None
    

class FileManager(object):
    
    def __init__(self, base_path=UPLOAD_FOLDER,
                    relative_path="",
                    namegen = None,
                    allowed_extensions=None,
                    permission=0o666, **kwargs):
        
        self.base_path = base_path
        self.relative_path = relative_path
        self.namegen = namegen or uuid_namegen
        self.allowed_extensions = allowed_extensions
        self.permission = permission
        self._should_delete = False
        
    
    def is_file_allowed(self, filename):
        if not self.allowed_extensions:
            return True
        return ('.' in filename and
                filename.rsplit('.', 1)[1].lower() in self.allowed_extensions)
    
    def generate_name(self, obj, file_data):
        return self.namegen(obj, file_data)

    def get_path(self, filename):
        if not self.base_path:
            raise ValueError('FileUploadField field requires base_path to be set.')
        return op.join(self.base_path, filename)

    def delete_file(self, filename):
        path = self.get_path(filename)
        if op.exists(path):
            os.remove(path)

    def save_file(self, data, filename):
        path = self.get_path(filename)
        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission)
        data.save(path)
        return filename

    
    
class ImageManager(FileManager):
    
    keep_image_formats = ('PNG',)
    
    def __init__(self,base_path=IMG_UPLOAD_FOLDER,
                    max_size=(300,200,True),
                    namegen = None,
                    relative_path=IMG_UPLOAD_URL,
                    allowed_extensions=None,
                    thumbgen=None, thumbnail_size=None,
                    permission=0o666,
                    **kwargs):

        # Check if PIL is installed
        if Image is None:
            raise Exception('PIL library was not found')

        self.max_size = max_size
        self.thumbnail_fn = thumbgen or thumbgen_filename
        self.thumbnail_size = thumbnail_size
        self.image = None
        
        if not allowed_extensions:
            allowed_extensions = ('gif', 'jpg', 'jpeg', 'png', 'tiff')

        super(ImageManager, self).__init__(base_path=base_path,
                                        relative_path=relative_path,
                                        namegen=namegen,
                                        allowed_extensions=allowed_extensions,
                                        permission=permission,
                                        **kwargs)

    def get_url(self, filename):
        return self.relative_path + filename
    
    # Deletion
    def delete_file(self, filename):
        super(ImageManager, self).delete_file(filename)

        self.delete_thumbnail(filename)

    def delete_thumbnail(self, filename):
        path = self.get_path(self.thumbnail_fn(filename))

        if op.exists(path):
            os.remove(path)

    # Saving
    def save_file(self, data, filename):
        if data and isinstance(data, FileStorage):
            try:
                self.image = Image.open(data)
            except Exception as e:
                raise ValidationError('Invalid image: %s' % e)
        
        path = self.get_path(filename)

        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission)

        # Figure out format
        filename, format = self.get_save_format(filename, self.image)
        print "IMG SAVE: ", filename,":", format, ":", self.max_size
        if self.image and (self.image.format != format or self.max_size):
            if self.max_size:
                image = self.resize(self.image, self.max_size)
            else:
                image = self.image
            self.save_image(image, self.get_path(filename), format)
        else:
            data.seek(0)
            data.save(path)
        self.save_thumbnail(data, filename, format)

        return filename

    def save_thumbnail(self, data, filename, format):
        if self.image and self.thumbnail_size:
            path = self.get_path(self.thumbnail_fn(filename))

            self.save_image(self.resize(self.image, self.thumbnail_size),
                             path,
                             format)

    def resize(self, image, size):
        print "RESIZE"
        (width, height, force) = size

        if image.size[0] > width or image.size[1] > height:
            if force:
                print "FORCE"
                return ImageOps.fit(self.image, (width, height), Image.ANTIALIAS)
            else:
                thumb = self.image.copy()
                thumb.thumbnail((width, height), Image.ANTIALIAS)
                return thumb

        return image

    def save_image(self, image, path, format='JPEG'):
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGBA')

        with open(path, 'wb') as fp:
            image.save(fp, format)

    def get_save_format(self, filename, image):
        if image.format not in self.keep_image_formats:
            name, ext = op.splitext(filename)
            filename = '%s.jpg' % name
            return filename, 'JPEG'
        return filename, image.format


def uuid_namegen(obj, file_data):
    return str(uuid.uuid1()) + '_sep_' + file_data.filename
    

def uuid_originalname(uuid_filename):
    return uuid_filename.split('_sep_')[1]
    
def thumbgen_filename(filename):
    name, ext = op.splitext(filename)
    return '%s_thumb%s' % (name, ext)
    
