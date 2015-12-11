#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2


# The follow sets up my jinja environment

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        self.render("MainPage.html")

class Stage1Lesson1(Handler):
    def get(self):
        self.render("Stage1Lesson1.html")

class Stage1Lesson2(Handler):
    def get(self):
        self.render("Stage1Lesson2.html")

class Stage1Lesson3(Handler):
    def get(self):
        self.render("Stage1Lesson3.html")

class Stage2Lesson1(Handler):
    def get(self):
        self.render("Stage2Lesson1.html")

class Stage2Lesson2(Handler):
    def get(self):
        self.render("Stage2Lesson2.html")

class Stage2Lesson3(Handler):
    def get(self):
        self.render("Stage2Lesson3.html")

class Stage2Lesson4(Handler):
    def get(self):
        self.render("Stage2Lesson4.html")

class Stage2Lesson5(Handler):
    def get(self):
        self.render("Stage2Lesson5.html")

class Stage2Lesson6(Handler):
    def get(self):
        self.render("Stage2Lesson6.html")

class Stage2Lesson7(Handler):
    def get(self):
        self.render("Stage2Lesson7.html")

class Stage4Lesson1(Handler):
    def get(self):
        self.render("Stage4Lesson1.html")

class Stage4Lesson2(Handler):
    def get(self):
        self.render("Stage4Lesson2.html")

class Stage4Lesson3(Handler):
    def get(self):
        self.render("Stage4Lesson3.html")

class Stage4Lesson4(Handler):
    def get(self):
        self.render("Stage4Lesson4.html")

class Stage4Lesson5(Handler):
    def get(self):
        self.render("Stage4Lesson5.html")

class Stage4Lesson6(Handler):
    def get(self):
        self.render("Stage4Lesson6.html")

class Stage4Lesson7(Handler):
    def get(self):
        self.render("Stage4Lesson7.html")

DEFAULT_WALL = 'Public'

# We set a parent key on the 'Post' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.

def wall_key(wall_name=DEFAULT_WALL):
  """Constructs a Datastore key for a Wall entity.

  We use wall_name as the key.
  """
  return ndb.Key('Wall', wall_name)

# These are the objects that will represent our Author and our Post. We're using
# Object Oriented Programming to create objects in order to put them in Google's
# Database. These objects inherit Googles ndb.Model class.
class Author(ndb.Model):
  """Sub model for representing an author."""
  identity = ndb.StringProperty(indexed=True)
  name = ndb.StringProperty(indexed=False)
  email = ndb.StringProperty(indexed=False)

class Post(ndb.Model):
  """A main model for representing an individual post entry."""
  author = ndb.StructuredProperty(Author)
  content = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)

class CommentsHandler(Handler):
  def get(self):
    wall_name = self.request.get('wall_name',DEFAULT_WALL)
    if wall_name == DEFAULT_WALL.lower(): wall_name = DEFAULT_WALL

    # Ancestor Queries, as shown here, are strongly consistent
    # with the High Replication Datastore. Queries that span
    # entity groups are eventually consistent. If we omitted the
    # ancestor from this query there would be a slight chance that
    # Greeting that had just been written would not show up in a
    # query.

    # [START query]
    posts_query = Post.query(ancestor = wall_key(wall_name)).order(-Post.date)

    # The function fetch() returns all posts that satisfy our query. The function returns a list of
    # post objects
    posts =  posts_query.fetch()
    # [END query]

    # If a person is logged into Google's Services
    user = users.get_current_user()
    if user:
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        user_name = user.nickname()
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        user_name = 'Anonymous Poster'

    # Create our posts html
    posts_html = ''
    for post in posts:

      # Check if the current signed in user matches with the author's identity from this particular
      # post. Newline character '\n' tells the computer to print a newline when the browser is
      # is rendering our HTML
      if user and user.user_id() == post.author.identity:
        posts_html += '<div><h3>(You) ' + post.author.name + '</h3>\n'
      else:
        posts_html += '<div><h3>' + post.author.name + '</h3>\n'

      posts_html += 'wrote: <blockquote>' + cgi.escape(post.content) + '</blockquote>\n'
      posts_html += '</div>\n'

    sign_query_params = urllib.urlencode({'wall_name': wall_name})

    # Write Out Page here
    self.render("comments.html", page_name="comments",  sqp=sign_query_params, wallname=cgi.escape(wall_name), 
                                    username=user_name, url=url, urllinktext=url_linktext, postshtml=posts_html)  

    # The following is the error handling for empty author or content fields, followed by the output.
    # user = Post.author
    # content = Post.content
    # if user is None or content is None:
    #     error = "'User' and 'Comment' can not be empty!"
    #     # With this approach, you can use the notification variable in your template for either instance
    #     self.render("comments.html", notification=error, sqp=sign_query_params, wallname=cgi.escape(wall_name), 
    #                                 username=user_name, url=url, urllinktext=url_linktext, postshtml=posts_html)
    # else:
    #     success = "Your comment has been added"
    #     self.render("comments.html", notification=success, sqp=sign_query_params, wallname=cgi.escape(wall_name), 
    #                                 username=user_name, url=url, urllinktext=url_linktext, postshtml=posts_html)
   
class PostWall(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Post' to ensure each
    # Post is in the same entity group. Queries across the
    # single entity group will be consistent. However, the write
    # rate to a single entity group should be limited to
    # ~1/second.
    wall_name = self.request.get('wall_name',DEFAULT_WALL)
    post = Post(parent=wall_key(wall_name))

    # When the person is making the post, check to see whether the person
    # is logged into Google
    if users.get_current_user():
      post.author = Author(
            identity=users.get_current_user().user_id(),
            name=users.get_current_user().nickname(),
            email=users.get_current_user().email())
    else:
      post.author = Author(
            name='anonymous@anonymous.com',
            email='anonymous@anonymous.com')

    # Get the content from our request parameters, in this case, the message
    # is in the parameter 'content'
    post.content = self.request.get('content')

    # Check if the current signed in user matches with the author's identity from this particular
    # post. Newline character '\n' tells the computer to print a newline when the browser is
    # is rendering our HTML
    user = post.author
    content = post.content
    if user is None or content is None:
        error = "'User' and 'Comment' can not be empty!"
        # With this approach, you can use the notification variable in your template for either instance
        self.rend("comments.html", notification=error, sqp=sign_query_params, wallname=cgi.escape(wall_name), 
                                    username=user_name, url=url, urllinktext=url_linktext, postshtml=posts_html)
    else:
        success = "Your comment has been added"
        self.redirect('/comments.html?wall_name=' + wall_name)
        # self.render("comments.html", notification=success, sqp=sign_query_params, wallname=cgi.escape(wall_name), 
        #                             username=user_name, url=url, urllinktext=url_linktext, postshtml=posts_html)

    # Write to the Google Database
    post.put()

    # Do other things here such as a page redirect
   
    #content = post.content
    # if post.content == "":
        #I'm not entirely sure what to type here. Everything I've tried has errored
    #     CommentsHandler.render("comments.html", error=error)
    # else:
    #     
    #self.redirect('/comments.html?wall_name=' + wall_name)




app = webapp2.WSGIApplication([("/", MainPage),
								("/Stage1Lesson1", Stage1Lesson1),
								("/Stage1Lesson2", Stage1Lesson2),
								("/Stage1Lesson3", Stage1Lesson3),
								("/Stage2Lesson1", Stage2Lesson1),
								("/Stage2Lesson2", Stage2Lesson2),
								("/Stage2Lesson3", Stage2Lesson3),
								("/Stage2Lesson4", Stage2Lesson4),
								("/Stage2Lesson5", Stage2Lesson5),
								("/Stage2Lesson6", Stage2Lesson6),
								("/Stage2Lesson7", Stage2Lesson7),
								("/Stage4Lesson1", Stage4Lesson1),
								("/Stage4Lesson2", Stage4Lesson2),
								("/Stage4Lesson3", Stage4Lesson3),
								("/Stage4Lesson4", Stage4Lesson4),
								("/Stage4Lesson5", Stage4Lesson5),
								("/Stage4Lesson6", Stage4Lesson6),
								("/Stage4Lesson7", Stage4Lesson7),
                                ("/comments.html", CommentsHandler),
                                ("/sign", PostWall)
								], debug=True)
