#-*-coding:utf-8 -*-
token = 'paste your token here'
current_todos={}

def pomotodo_get_completed_todos_from_todoist():
    pomotodo_todos=[]
    import requests
    from datetime import datetime,date,timedelta

    start_date = 'normal'
    if start_date == 'normal':
        start_date=datetime.today()-timedelta(hours=100)
        start_date=str(start_date.date())
    start_date=datetime.strptime(start_date,'%Y-%m-%d')

    response = requests.get('https://api.pomotodo.com/1/todos', headers={'Authorization': token}
                            , params={'limit':100,'completed_later_than':start_date,'completed':True})
    pomotodo_todos+=response.json()
    try:
        url_next=response.links['next']['url']
        while True:
            response = requests.get('https://api.pomotodo.com'+url_next, headers={'Authorization': token}
            , params = {'limit': 100, 'completed_later_than': start_date, 'completed': True})
            pomotodo_todos+=response.json()
            try:
                url_next=response.links['next']['url']
                print url_next
            except:
                break
    except:
        pass

    todoist_in_here={}
    for i in pomotodo_todos:
        try:
            id = i['notice']
            if id not in [None,'']:
                todo= i['description']
                completed= i["completed"]
                todoist_in_here.update({id:{'todo':todo,'completed':completed,'id':id}})
        except:
            print 'what the fuck? probably dosent have ids'
    return todoist_in_here

def pomotodo_get_uncompleted_todos_from_todoist():
    pomotodo_todos=[]
    import requests
    from datetime import datetime,date,timedelta

    start_date = 'normal'
    if start_date == 'normal':
        start_date=datetime.today()-timedelta(hours=100)
        start_date=str(start_date.date())
    start_date=datetime.strptime(start_date,'%Y-%m-%d')

    response = requests.get('https://api.pomotodo.com/1/todos', headers={'Authorization': token}
                            , params={'limit':100,'completed':False})
    pomotodo_todos+=response.json()
    try:
        url_next=response.links['next']['url']
        while True:
            response = requests.get('https://api.pomotodo.com'+url_next, headers={'Authorization': token}
            , params = {'limit': 100,'completed': False})
            pomotodo_todos+=response.json()
            try:
                url_next=response.links['next']['url']
                print url_next
            except:
                break
    except:
        pass

    todoist_in_here={}
    for i in pomotodo_todos:
        if not i['notice'] == None:
            id= i['notice']
            todo= i['description']
            completed= i["completed"]
            todoist_in_here.update({id:{'todo':todo,'completed':completed,'id':id}})

    return todoist_in_here

def pomotodo_addtodos_from_todoist(today_todo_name,deadline,item_para_dict):
    import requests, sys, json
    reload(sys)  # Reload does the trick!
    sys.setdefaultencoding('UTF-8')
    import pytz,datetime
    tz = pytz.timezone('Asia/Shanghai')
    today_dttm=datetime.datetime.now(tz)
    nodeadline=False

    if deadline == 'today':
        deadline=today_dttm.replace(hour=22, minute=30)
        deadline=deadline.isoformat()
    elif deadline=='none':
        nodeadline=True
    else:
        deadline=datetime.datetime.strptime(deadline,'%Y-%m-%d')
        deadline=deadline.replace(hour=22, minute=30).replace(tzinfo=tz)
        deadline=deadline.isoformat()

     # past todos
    response = requests.get('https://api.pomotodo.com/1/todos', headers={'Authorization': token})

    global current_todos

    current_ids=[]
    pomotodo_todos=[]
    pomotodo_todos += response.json()

    for j in pomotodo_todos:
        notice=str(j['notice'])
        uuid=str(j['uuid'])
        name=str(j["description"])

        if not notice in ['','None']:
            current_ids.append(notice)
            current_todos.update({uuid:notice})

    today_todo_name_id = sorted(today_todo_name.keys(), key=lambda x: item_para_dict[x]['item_order'])

    # append todos to web
    for id in today_todo_name_id:
        if 'Inbox' in today_todo_name[id]:
            print today_todo_name[id]
            continue

        if not str(id) in current_ids:
            if nodeadline:
                data={'description':today_todo_name[id],
                      'notice':str(id)}
            else:
                data={'description':today_todo_name[id],
                      'remind_time':deadline,
                      'notice':str(id)}
            response = requests.post('https://api.pomotodo.com/1/todos', json=data, headers={'Authorization': token,"Content-Type":"application/json"})
            print response.status_code
        else:
            print 'already exsits'

def pomotodo_todoist_del_extra_todos(today_todo_name,item_para_dict):
    today_todo_name_id = sorted(today_todo_name.keys(), key=lambda x: item_para_dict[x]['item_order'])
    import requests
    todel_repetitive_uuid=[]
    exist_ids=[]
    for uuid in current_todos.keys():
        id = current_todos[uuid]
        if id in exist_ids:
            todel_repetitive_uuid.append(uuid)
        else:
            exist_ids.append(id)

    for uuid in current_todos.keys():
        id = current_todos[uuid]

        if uuid in todel_repetitive_uuid:
            data={
                # 'uuid':uuid,
                'notice':'',
                'completed':'true',
            }
            response = requests.patch('https://api.pomotodo.com/1/todos/' + uuid,json=data, headers={'Authorization': token})
            print 'todo deleted', response.status_code, uuid

        if not int(id) in today_todo_name_id:
            data={
                # 'uuid':uuid,
                'notice':'',
                'completed':'true',
            }
            response = requests.patch('https://api.pomotodo.com/1/todos/' + uuid,json=data, headers={'Authorization': token})
            print 'todo deleted', response.status_code, uuid
