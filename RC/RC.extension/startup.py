import os 
import sys

from pyrevit import HOST_APP, framework
from pyrevit import revit, DB
from pyrevit import forms

# define event handler
def docopen_eventhandler(sender, args):
    forms.alert('Document Opened: {}'.format(args.PathName))

# add the event handler function
HOST_APP.app.DocumentOpening += \
    framework.EventHandler[DB.Events.DocumentOpeningEventArgs](
        docopen_eventhandler
        )

#Set Project Path
from pyrevit.userconfig import user_config
for ext_path in user_config.get_ext_root_dirs():
    path = os.path.abspath(os.path.join(ext_path,  os.pardir))
    sys.path.append(path)

