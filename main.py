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

import wsgiref.handlers, logging, email
import cgi, sys, time, datetime
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.util import login_required

# They are changing Django version, need to include this
# http://code.google.com/appengine/docs/python/tools/libraries.html#Django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '0.96')


from usermodels import *

#   Routes
#   /
#   /add_event
#   /add_event_later
#   /add_reminder
#   /history
#   /delete_event
#   /delete_contact
#   /login
#   /report/([^/]+)?
#   /printfriendly
#   /update_star
#   /add_post

#   Decorators
#   @login_required


class add_post(webapp.RequestHandler):
  def post(self):
    
    entries = Contacts()
    entries.name = self.request.get("name")
    entries.company = self.request.get("company")
    entries.customer_type = self.request.get("customer_type")
    entries.office = self.request.get("office")
    entries.cell = self.request.get("cell")
    entries.email = self.request.get("email")
    entries.address = self.request.get("address")
    entries.put()
    self.redirect("/")


class add_event(webapp.RequestHandler):
  def post(self):
    
    keyname = self.request.get("key")
    title = self.request.get("title")
    content = self.request.get("content")
    date = self.request.get("date")
    self.redirect("/")
    
    # Yay! start the async coolness
    mem_key = memcache.get(keyname)
    if mem_key is not None:
      memcache.delete(str(mem_key))
    
    taskqueue.add(url='/add_event_later', params={'key':keyname, 'title':title, 'content':content, 'date':date})
    

class add_event_later(webapp.RequestHandler):
    # called from taskqueue
    def post(self):
      
      if isLocal():
        logging.info("Task Queue is adding event")
      
      updated = []
        
      event = Events()
      event.key_of_parent = self.request.get('key')
      event.title = self.request.get('title')
      event.content = self.request.get('content')
      event.date = self.request.get('date')
      updated.append(event)
        
      entry = Contacts().get(self.request.get('key'))
      if entry:
        entry.last_contact = self.request.get('date')
        entry.last_item = self.request.get('content')
        updated.append(entry)
      
      db.put(updated)
      logging.info("Database has been update from queue")



class add_reminder(webapp.RequestHandler):
  def post(self):
    
    updated = []
    
    reminder = Reminders()
    keyname = self.request.get("key")
    reminder.key_of_parent = keyname
    reminder.title = self.request.get("title")
    reminder.content = self.request.get("content")
    reminder.date = self.request.get("date")
    reminder.email = self.request.get("email")
    updated.append(reminder)
    
    entry = Contacts().get(keyname)
    if entry:
      entry.next_item_due = self.request.get("date")
      entry.next_item = self.request.get("content")
      updated.append(entry)
    
    db.put(updated)
    self.redirect("/")
    
class delete_event(webapp.RequestHandler):
  @login_required
  def get(self):
    
    keyname = self.request.get("delete_key")

    event = Events().get(keyname)
    if event:
      event.delete()
    
    
class delete_contact(webapp.RequestHandler):
  @login_required
  def get(self):
    
    keyname = self.request.get("delete_key")

    contact = Contacts().get(keyname)
    if contact:
      contact.delete()
    
        
class update_star(webapp.RequestHandler):
  @login_required
  def get(self):
    
    keyname = self.request.get("star_key")

    contact = Contacts().get(keyname)
    if contact:
      if contact.star != "star_on":
        contact.star = "star_on"
        contact.put()
      else:
        contact.star = "star_off"
        contact.put()
        
    # self.response.out.write(contact.star)
    # getting all ajax-y so I don't need this
    #self.redirect("/")
            
        
class ajaxHistory(webapp.RequestHandler):
  @login_required
  def get(self):
    
    key_name = self.request.get('key')
    mem_key = memcache.get(key_name)
    if mem_key is not None:
      render_template(self, 'templates/_history.html', mem_key)
    else:
      events = Events.gql("WHERE key_of_parent = :1 order by actual_date DESC", key_name) 
    
      template_values = {
         'events': events,
         'key_name': key_name
         }
      memcache.add(key_name, template_values)
   
      render_template(self, 'templates/_history.html', template_values)


class login(webapp.RequestHandler):
  @login_required
  def get(self):
    render_template(self, 'templates/login.html', {})
    
     
#  Need to clean this up.  Make it use pretty URLs and memcache

class MainHandler(webapp.RequestHandler):
  @login_required
  def get(self):

    if users.is_current_user_admin():
      
      items_per_page = 10                 #how many items to fetch per page
      sortby = self.request.get("o")
      filter = self.request.get("filter")
      raw_offset = self.request.get("offset")
      if raw_offset:
        offset = int(raw_offset)
      else:
        offset = 0
      if sortby == '0':
        count = Contacts.gql("order by modified_date DESC").count()
        entries = Contacts.gql("order by modified_date DESC").fetch(items_per_page, offset) #show newest on top, default sort option
      if sortby == '1':
        count = Contacts.gql("order by modified_date").count()
        entries = Contacts.gql("order by modified_date").fetch(items_per_page, offset)      #show oldest on top
      elif sortby == '2':
        count = Contacts.gql("order by company ASC").count()
        entries = Contacts.gql("order by company ASC").fetch(items_per_page, offset)        #show by company name
      elif sortby == '3':
        count = Contacts.gql("order by customer_type").count()
        entries = Contacts.gql("order by customer_type").fetch(items_per_page, offset)      #show by customer type
      elif sortby == '4':
        count = Contacts.gql("where star = :1", "star_on").count()
        entries = Contacts.gql("where star = :1", "star_on").fetch(items_per_page, offset)  #only show items that have been starred
      elif sortby == '-1':                                    #this is how I am using the breaking out of sort types
        if filter:
          count = Contacts.gql("where customer_type = :1", filter).count()
          entries = Contacts.gql("where customer_type = :1", filter).fetch(items_per_page, offset)
        else:
          count = 0
          entries = None
      elif sortby == '-2':                                    #this is how I am using the breaking out of sort types
        if filter:
          count = Contacts.gql("where company = :1", filter).count()
          entries = Contacts.gql("where company = :1", filter).fetch(items_per_page, offset)
        else:
          count = 0
          entries = None
      else:
        count = Contacts.gql("order by modified_date DESC").count()
        entries = Contacts.gql("order by modified_date DESC").fetch(items_per_page, offset) #show newest on top, default sort option
    
      if count > (len(entries) + offset):
        show_text = True
        new_offset = offset + items_per_page      #this is what the next URL uses for offset
      else:
        show_text = False
        new_offset = 0
    
      user = users.get_current_user()
      if user:
        login_url = users.create_logout_url("/")
      else:
        login_url = users.create_login_url("/")
    
      template_values = {
        'login_url': login_url,
        'items_per_page': items_per_page,
        'count': count,
        'show_text': show_text,
        'offset': offset + 1,                      #fix for zero index, make readable
        'new_offset': new_offset,                  #this is what the next URL uses for offset
        'sortby': sortby, 
        'filter': filter,
        'entries': entries,
        'entries_len': len(entries) + offset  #shows how many items we fetched, and their positions
        }
      
      render_template(self, 'templates/base.html', template_values)
    else:
    
      user = users.get_current_user()
      if user:
        login_url = users.create_logout_url("/")
      else:
        login_url = users.create_login_url("/")
        
      render_template(self, 'templates/404.html', {'login_url': login_url})

def isLocal():
    return os.environ["SERVER_NAME"] in ("localhost")    

    
def render_template(call_from, template_name, template_values=dict()):
  path = os.path.join(os.path.dirname(__file__), template_name)
  call_from.response.out.write(template.render(path, template_values))

    
def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/index', MainHandler), #keep this for pagination
                                        ('/add_event', add_event),
                                        ('/add_event_later', add_event_later),
                                        ('/add_reminder', add_reminder),
                                        ('/history', ajaxHistory),
                                        ('/delete_event', delete_event),
                                        ('/delete_contact',delete_contact),
                                        ('/login', login),
                                        ('/update_star', update_star),
                                        ('/add_post', add_post)],
                                         debug = isLocal())
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
