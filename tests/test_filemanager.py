import io
import os
import os.path as op
import shutil
import tempfile
import unittest

from flask import Flask
from flask_appbuilder.filemanager import FileManager, ImageManager
from PIL import Image
from werkzeug.datastructures import FileStorage


def png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), (255, 0, 0)).save(buf, "PNG")
    return buf.getvalue()


def file_storage(filename, data=None):
    return FileStorage(io.BytesIO(data or png_bytes()), filename=filename)


class FileManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.upload_folder = op.join(self.base, "uploads")
        self.outside_folder = op.join(self.base, "static")
        os.makedirs(self.upload_folder)
        os.makedirs(self.outside_folder)

        self.app = Flask(__name__)
        self.app.config["UPLOAD_FOLDER"] = self.upload_folder + "/"
        self.app.config["IMG_UPLOAD_FOLDER"] = self.upload_folder + "/"
        self.app.config["IMG_UPLOAD_URL"] = "/static/uploads/"
        self.app.config["IMG_SIZE"] = (300, 200, True)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()
        shutil.rmtree(self.base, ignore_errors=True)

    def uploaded_files(self):
        return sorted(
            op.relpath(op.join(root, name), self.base)
            for root, _, names in os.walk(self.base)
            for name in names
        )

    def test_file_manager_save_file(self):
        """FileManager: save file keeps the given name"""
        fm = FileManager()
        filename = fm.save_file(file_storage("doc.txt"), "uuid_sep_doc.txt")

        self.assertEqual(filename, "uuid_sep_doc.txt")
        self.assertEqual(self.uploaded_files(), ["uploads/uuid_sep_doc.txt"])

    def test_file_manager_save_file_relative_name(self):
        """FileManager: save file with a relative name stays on the upload folder"""
        fm = FileManager()
        filename = fm.save_file(
            file_storage("doc.txt"), "uuid_sep_../../static/doc.txt"
        )

        self.assertEqual(filename, "uuid_sep_.._.._static_doc.txt")
        self.assertEqual(self.uploaded_files(), ["uploads/" + filename])

    def test_image_manager_save_file(self):
        """ImageManager: save file keeps the given name"""
        im = ImageManager(thumbnail_size=(30, 30, True))
        filename = im.save_file(file_storage("photo.png"), "uuid_sep_photo.png")

        self.assertEqual(filename, "uuid_sep_photo.png")
        self.assertEqual(
            self.uploaded_files(),
            ["uploads/uuid_sep_photo.png", "uploads/uuid_sep_photo_thumb.png"],
        )

    def test_image_manager_save_file_relative_name(self):
        """ImageManager: save file with a relative name stays on the upload folder"""
        im = ImageManager(thumbnail_size=(30, 30, True))
        filename = im.save_file(
            file_storage("photo.png"), "uuid_sep_../../static/new/photo.png"
        )

        self.assertEqual(filename, "uuid_sep_.._.._static_new_photo.png")
        self.assertEqual(
            self.uploaded_files(),
            [
                "uploads/" + filename,
                "uploads/uuid_sep_.._.._static_new_photo_thumb.png",
            ],
        )
        self.assertFalse(op.exists(op.join(self.outside_folder, "new")))

    def test_image_manager_save_file_relative_name_no_size(self):
        """ImageManager: save file with a relative name does not overwrite"""
        existing = op.join(self.outside_folder, "logo.png")
        with open(existing, "wb") as fp:
            fp.write(b"ORIGINAL")

        im = ImageManager()
        im.max_size = None
        filename = im.save_file(
            file_storage("logo.png"), "uuid_sep_../../static/logo.png"
        )

        self.assertEqual(filename, "uuid_sep_.._.._static_logo.png")
        with open(existing, "rb") as fp:
            self.assertEqual(fp.read(), b"ORIGINAL")
        self.assertEqual(
            self.uploaded_files(), ["static/logo.png", "uploads/" + filename]
        )

    def test_image_manager_save_file_absolute_name(self):
        """ImageManager: save file with an absolute name stays on the upload folder"""
        im = ImageManager(thumbnail_size=(30, 30, True))
        filename = im.save_file(
            file_storage("photo.png"),
            "uuid_sep_" + op.join(self.outside_folder, "a.png"),
        )

        self.assertNotIn(os.sep, filename)
        self.assertEqual(
            self.uploaded_files(),
            [
                "uploads/" + filename,
                "uploads/" + filename.replace(".png", "_thumb.png"),
            ],
        )
