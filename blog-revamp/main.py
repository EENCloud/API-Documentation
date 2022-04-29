#!/usr/bin/env python


import os

import jinja2
import webapp2

from google.appengine.ext.webapp import template

from google.appengine.api import users

from usermodels import *  #I'm storing my models in usermodels.py
from handlers import *


def isLocal():
    return os.environ["SERVER_NAME"] in ("localhost")

app = webapp2.WSGIApplication([('/', BlogHandler),
                                ('/delete/([^/]+)?', DeleteHandler),
                                ('/blog', BlogHandler),
                                ('/blog/([^/]+)?', BlogHandler),
                                ('/partial/([^/]+)?', PartialHandler),
                                ('/edit', BlogHandler),
                                ('/edit/([^/]+)?', EditHandler),
                                ('/post', BlogHandler),
                                ('/post/([^/]+)?', PostHandler),
                                ('/export', ExportHandler),
                                ('/new', CreateHandler),
                                ('/upload_img', ImgUploadHandler),
                                ('/login', LoginHandler),
                                ('/logout', LogoutHandler)],
                                 debug=isLocal())
