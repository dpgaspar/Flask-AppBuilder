import os
import re
import uuid
import logging
import os.path as op

from flask.globals import _request_ctx_stack
from wtforms import ValidationError
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage

try:
    from flask import _app_ctx_stack
except ImportError:
    _app_ctx_stack = None

app_stack = _app_ctx_stack or _request_ctx_stack

log = logging.getLogger(__name__)

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None


class FileManager(object):
    def __init__(self, base_path=None,
                 relative_path='',
                 namegen=None,
                 allowed_extensions=None,
                 permission=0o666, **kwargs):


        ctx = app_stack.top

        if 'UPLOAD_FOLDER' in ctx.app.config and not base_path:
            base_path = ctx.app.config['UPLOAD_FOLDER']
        if not base_path:
            raise Exception('Config key UPLOAD_FOLDER is mandatory')

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
        return self.namegen(file_data)

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

    def __init__(self, base_path=None,
                 relative_path=None,
                 max_size=None,
                 namegen=None,
                 allowed_extensions=None,
                 thumbgen=None, thumbnail_size=None,
                 permission=0o666,
                 **kwargs):

        # Check if PIL is installed
        if Image is None:
            raise Exception('PIL library was not found')

        ctx = app_stack.top
        if 'IMG_SIZE' in ctx.app.config and not max_size:
            max_size = ctx.app.config['IMG_SIZE']
        self.max_size = max_size or (300, 200, True)

        if 'IMG_UPLOAD_URL' in ctx.app.config and not relative_path:
            relative_path = ctx.app.config['IMG_UPLOAD_URL']
        if not relative_path:
            raise Exception('Config key IMG_UPLOAD_URL is mandatory')

        if 'IMG_UPLOAD_FOLDER' in ctx.app.config and not base_path:
            base_path = ctx.app.config['IMG_UPLOAD_FOLDER']
        if not base_path:
            raise Exception('Config key IMG_UPLOAD_FOLDER is mandatory')

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
        if isinstance(filename, FileStorage):
            return filename.filename
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
        (width, height, force) = size

        if image.size[0] > width or image.size[1] > height:
            if force:
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


def uuid_namegen(file_data):
    return str(uuid.uuid1()) + '_sep_' + file_data.filename


def get_file_original_name(name):
    """
        Use this function to get the user's original filename.
        Filename is concatenated with <UUID>_sep_<FILE NAME>, to avoid collisions.
        Use this function on your models on an aditional function

        ::

            class ProjectFiles(Base):
                id = Column(Integer, primary_key=True)
                file = Column(FileColumn, nullable=False)

                def file_name(self):
                    return get_file_original_name(str(self.file))

        :param name:
            The file name from model
        :return:
            Returns the user's original filename removes <UUID>_sep_
    """
    re_match = re.findall('.*_sep_(.*)', name)
    if re_match:
        return re_match[0]
    else:
        return 'Not valid'


def uuid_originalname(uuid_filename):
    return uuid_filename.split('_sep_')[1]


def thumbgen_filename(filename):
    name, ext = op.splitext(filename)
    return '%s_thumb%s' % (name, ext)
    
