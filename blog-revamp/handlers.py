
import os

import jinja2
import webapp2

from google.appengine.ext.webapp import template

from google.appengine.api import users

from usermodels import *  #I'm storing my models in usermodels.py


class MainHandler(webapp2.RequestHandler):
  def get(self):
    render_template(self, 'templates/index.html')


class PartialHandler(webapp2.RequestHandler):
  def get(self, resource=''):
    #Did anything come in on the url /partial/:resource
    if resource:
      posts = Blog().gql("where tag = :1 order by date desc", resource).fetch(1)
      if posts:
        for p in posts:
          self.response.out.write('<div class=\"block-3\" id=\"partial\"><p>' + p.content + '</p></div>')
      else:
        self.response.out.write('There is nothing in the database about ' + resource)
    else:
      self.response.out.write('Content not found')


class DeleteHandler(webapp2.RequestHandler):
  def get(self, resource=''):
    #check if there is a key
    if resource:
      #check if they are allowed to delete things
      if users.is_current_user_admin():
        b = Blog().get(resource)
        if b:
          b.delete()

    self.redirect("/blog")

class BlogHandler(webapp2.RequestHandler):
  def get(self, resource=''):

    #Check to see if user is an admin, and display correct link
    admin = users.is_current_user_admin()
    if admin:
      admin_url = users.create_logout_url("/blog")
      admin_url_text = 'Logout'
    else:
      admin_url = users.create_login_url("/blog")
      admin_url_text = 'Login'

    #Did anything come in on the url /blog/:resource
    if resource:
      posts = Blog().gql("where tag = :1 order by date desc", resource).fetch(30)
      if len(posts) == 0:
        posts = Blog().gql("order by date desc").fetch(50)
    else:
      posts = Blog().gql("order by date desc").fetch(30)

    #Build the SideBar
    tags = SideBar().gql("order by title asc")
    tags_list = []
    for t in tags:
      tags_list.append(t.title)


    template_values = {
      'tags': list(set(tags_list)),
      'resource': resource,
      'posts': posts,
      'admin': admin,
      'admin_url': admin_url,
      'admin_url_text': admin_url_text
    }

    render_template(self, 'templates/blog.html', template_values)


  def post(self, resource):
    if users.is_current_user_admin():
      b = Blog()
      s = SideBar()
      b.title = self.request.get("title")
      b.content = self.request.get("html_body")
      b.markdown = self.request.get("user_input")
      b.author = self.request.get('author')
      b.content_img = self.request.get('content_img')
      b.teaser = self.request.get('teaser')
      b.tag = self.request.get("category").lower()
      s.path = self.request.get("category").lower()
      s.title = self.request.get("category").lower()
      #this is weird, but this is a batch put to the datastore
      updated = []
      updated.append(b)
      updated.append(s)
      db.put(updated)

    self.redirect("/blog")


class EditHandler(webapp2.RequestHandler):
  def get(self, resource=''):
    #Check to see if user is an admin, and display correct link
    admin = users.is_current_user_admin()
    if admin:
      admin_url = users.create_logout_url("/blog")
      admin_url_text = 'Logout'
    else:
      admin_url = users.create_login_url("/blog")
      admin_url_text = 'Login'

    #reject anything that doesn't have a key
    if resource == '' or not admin:
      self.redirect("/blog")

    else:
      p = Blog().get(resource)
      if p is None:
        self.redirect('/blog')
      else:
        template_values = {
          'resource': resource,
          'p': p,
          'admin': admin,
          'admin_url': admin_url,
          'admin_url_text': admin_url_text
          }

        render_template(self, 'templates/edit.html', template_values)


  def post(self, resource=''):
    #Check to see if user is an admin, and display correct link
    admin = users.is_current_user_admin()
    if admin:
      admin_url = users.create_logout_url("/blog")
      admin_url_text = 'Logout'
    else:
      admin_url = users.create_login_url("/blog")
      admin_url_text = 'Login'

    #reject anything that doesn't have a key
    if resource == '':
      self.redirect("/blog")

    b = Blog().get(resource)
    #check if it found anything
    if b:
      b.title = self.request.get("title")
      b.content = self.request.get("html_body")
      if self.request.get('content_img'):
        b.content_img = self.request.get('content_img')
      if self.request.get('teaser'):
        b.teaser = self.request.get('teaser')
      if self.request.get('author'):
        b.author = self.request.get('author')
      b.markdown = self.request.get("user_input")
      b.tag = self.request.get("category").lower()
      b.put()

    self.redirect("/blog")


class PostHandler(webapp2.RequestHandler):
  def get(self, resource=''):
    #Check to see if user is an admin, and display correct link
    admin = users.is_current_user_admin()
    if admin:
      admin_url = users.create_logout_url("/blog")
      admin_url_text = 'Logout'
    else:
      admin_url = users.create_login_url("/blog")
      admin_url_text = 'Login'

    #reject anything that doesn't have a key
    if resource == '':
      self.redirect("/blog")

    else:
      p = Blog().get(resource)
      template_values = {
        'resource': resource,
        'p': p,
        'admin': admin,
        'admin_url': admin_url,
        'admin_url_text': admin_url_text
        }

      render_template(self, 'templates/post.html', template_values)



class ExportHandler(webapp2.RequestHandler):
  def get(self, resource=''):

    #Check to see if user is an admin, and display correct link
    admin = users.is_current_user_admin()
    if admin:
      admin_url = users.create_logout_url("/blog")
      admin_url_text = 'Logout'
    else:
      admin_url = users.create_login_url("/blog")
      admin_url_text = 'Login'

    #Did anything come in on the url /blog/:resource
    if resource:
      posts = Blog().gql("where tag = :1 order by date desc", resource).fetch(1000)
      if len(posts) == 0:
        posts = Blog().gql("order by date desc").fetch(1000)
    else:
      posts = Blog().gql("order by date desc").fetch(1000)

    #Build the SideBar
    tags = SideBar().gql("order by title asc")
    tags_list = []
    for t in tags:
      tags_list.append(t.title)


    template_values = {
      'tags': list(set(tags_list)),
      'resource': resource,
      'posts': posts,
      'admin': admin,
      'admin_url': admin_url,
      'admin_url_text': admin_url_text
    }

    self.response.headers['Content-Type'] = 'application/rss+xml'
    render_template(self, 'templates/rss.html', template_values)



class CreateHandler(webapp2.RequestHandler):
  def get(self, resource=''):

    #Check to see if user is an admin, and display correct link
    admin = users.is_current_user_admin()
    user = users.get_current_user()
    if admin:
      admin_url = users.create_logout_url("/blog")
      admin_url_text = 'Logout'
    else:
      admin_url = users.create_login_url("/blog")
      admin_url_text = 'Login'

    template_values = {
      'admin': admin,
      'admin_url': admin_url,
      'admin_url_text': admin_url_text
    }

    render_template(self, 'templates/new.html', template_values)


  def post(self, resource):
    if users.is_current_user_admin():
      b = Blog()
      s = SideBar()
      b.title = self.request.get("title")
      b.content = self.request.get("html_body")
      b.markdown = self.request.get("user_input")
      b.author = self.request.get('author')
      b.content_img = self.request.get('content_img')
      b.teaser = self.request.get('teaser')
      b.tag = self.request.get("category").lower()
      s.path = self.request.get("category").lower()
      s.title = self.request.get("category").lower()
      #this is weird, but this is a batch put to the datastore
      updated = []
      updated.append(b)
      updated.append(s)
      db.put(updated)

    self.redirect("/blog")

class ImgUploadHandler(webapp2.RequestHandler):
  def get(self, resource=''):
    #Check to see if user is an admin, and display correct link
    admin = users.is_current_user_admin()
    user = users.get_current_user()
    if admin:
      admin_url = users.create_logout_url("/blog")
      admin_url_text = 'Logout'
    else:
      admin_url = users.create_login_url("/blog")
      admin_url_text = 'Login'

    template_values = {
      'admin': admin,
      'admin_url': admin_url,
      'admin_url_text': admin_url_text
    }

    render_template(self, 'templates/upload.html', template_values)

  def post(self, resource):
    pass


class LoginHandler(webapp2.RequestHandler):
  def get(self, resource=''):
    admin_url = users.create_login_url("/blog")
    self.redirect(admin_url)

class LogoutHandler(webapp2.RequestHandler):
  def get(self, resource=''):
    admin_url = users.create_logout_url("/blog")
    self.redirect(admin_url)



def render_template(call_from, template_name, template_values=dict()):
  path = os.path.join(os.path.dirname(__file__), template_name)
  call_from.response.out.write(template.render(path, template_values))