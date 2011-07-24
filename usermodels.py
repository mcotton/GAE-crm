from google.appengine.ext import db

class Contacts(db.Model):
  name = db.StringProperty()
  company = db.StringProperty()
  customer_type = db.StringProperty(default="Misc")
  last_contact = db.StringProperty()
  last_item = db.TextProperty()
  next_item = db.TextProperty()
  next_item_due = db.StringProperty()
  modified_date = db.DateTimeProperty(auto_now=True)
  office = db.StringProperty()
  cell = db.StringProperty()
  email = db.StringProperty()
  address = db.StringProperty()
  star = db.StringProperty(default="star_off")
  latitude = db.StringProperty(default="29.611986")
  longitude = db.StringProperty(default="-98.4883264")
  
class Events(db.Model):
  key_of_parent = db.StringProperty()
  title = db.StringProperty()
  content = db.TextProperty()
  actual_date = db.DateTimeProperty(auto_now=True)
  date = db.StringProperty()
  reported = db.StringProperty(default="False")
  
class Reminders(db.Model):
  key_of_parent = db.StringProperty()
  title = db.StringProperty()
  content = db.TextProperty()
  actual_date = db.DateTimeProperty(auto_now=True)
  date = db.StringProperty()
  email = db.StringProperty()