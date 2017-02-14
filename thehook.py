#!/usr/bin/env/ python
print "Content-type: text/html"
import cgitb
cgitb.enable()
import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF-8')
print "Content-type:text/html"
import todoist
from functions import *
from pomotodo_api import *

token = 'paste your todoist token here'
api = todoist.TodoistAPI(token)

###  **********  pomotodo update todoist

    #############    pomotodo complete todoist
completed_todos_from_todoist=pomotodo_get_completed_todos_from_todoist()
for id in completed_todos_from_todoist:
    try:
        item = api.items.get_by_id(int(id))
        item.complete()
        api.commit()
    except:
        print 'not in todoist'


###  **********  todoist update pomotodo
api.sync()
update_todoist(api)
for id in today_todo_id:
    get_full_todo_for_pomotodo(id)
    #############   todoist add todos to pomotodo
for id in today_todo_name:
    print '<h2>',id,today_todo_name[id],'</h2>'
pomotodo_addtodos_from_todoist(today_todo_name,'today',item_para_dict)

    ############# delete extra todos
pomotodo_todoist_del_extra_todos(today_todo_name,item_para_dict)


print '<h2>done running</h2>'
print '</body>'
print '</html>'
