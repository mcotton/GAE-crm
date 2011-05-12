## Quick start python template for Google App Engine ##

You'll need to do several things before your first deploy.

*First*: open up app.yaml and replace 'app' with yourn app name

>  application: app

*Second*: remember to update the version line, trust me, it'll be helpfull when
you deploy.  Make sure to mention/tag the git log with the deployed version.

>  version: app-1

*Third*:  make sure to version your local datastore.  I can not think of any
reason not to do this.
Depending on what platform you use, you will need to add these flags when your
app starts in the development console.

>  --datastore_path=/Users/cotton/dev/clean/datastore

*Fourth*: your models live in usermodels.py

*Fifth*: if you want to use some other Django template, change these lines in
main.py

>  import os
>  os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
>  from google.appengine.dist import use_library
>  use_library('django', '0.96')


*Please fork and contribute your own hacks*

