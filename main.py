#!/usr/bin/env python

#  Routes
#  /
#  

#  Decorators
#  @login_required

import wsgiref.handlers, logging
import cgi, time, datetime
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#  from google.appengine.ext.webapp.util import login_required
#  from google.appengine.api import users
#  from google.appengine.api import mail
#  from google.appengine.api import memcache
#  from google.appengine.api import taskqueue

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '0.96')

from usermodels import *  #I'm storing my models in usermodels.py


class MainHandler(webapp.RequestHandler):
  def get(self):
    render_template(self, 'templates/index.html')

def is_local():
  # Turns on debugging error messages if on local env  
  return os.environ["SERVER_NAME"] in ("localhost")  
    
def render_template(call_from, template_name, template_values=dict()):
  # Makes rendering templates easier.
  path = os.path.join(os.path.dirname(__file__), template_name)
  call_from.response.out.write(template.render(path, template_values))

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug = is_local())
                                         
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
