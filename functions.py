#-*-coding:utf-8 -*-
import datetime,pytz,pprint
tz = pytz.timezone('Asia/Shanghai')
today_dttm=datetime.datetime.now(tz)
today_date_str=today_dttm.date()
today_todo_name={}
today_todo_id,item_para_dict,=[],{}

#更新todoist 数据,获得今日所有的todo(未完成)
def update_todoist(api):
    ### *** list all projects *** ###
    global parent_project_id, project_name
    projects = api.projects.all()

    projects_id = {} #give name produce id
    project_name = {} # give id produce name
    project_indent = {} # give id produce ident

    parent_project_id = {} # give id produce parent id
    for i in projects:
        name = i['name']
        id = i['id']
        indent = i['indent']
        parent_id = i['parent_id']

        projects_id.update({name: id})
        project_name.update({id: name})
        project_indent.update({id: indent})

        if not parent_id == None:
            parent_project_id.update({id: parent_id})
        else:
            parent_project_id.update({id: id})

    global item_para_dict, item_dict,today_todo_id
    ### *** list all items *** ###
    items = api.items.all()
    item_dict = {} #give project id produce whole items
    for i in items:
        name = i['content']
        id = i['id']
        project_id = i['project_id']
        indent = i['indent']
        item_order = i['item_order']
        deadline=i['due_date_utc']
        checked=i['checked']

        ### update item_para_dict
        item_para_dict.update({id: {'name': name,
                                    'project_id': project_id,
                                    'checked':checked,
                                    'item_order':item_order}})

        ### update today_todo_id (get all today ids complete or not)
        if not deadline in [None,"",'None'] :
            deadline = datetime.datetime.strptime(deadline[:-15], '%a %d %b %Y').date()
            if deadline == today_date_str:
                if checked == 0:
                    today_todo_id.append(id)

        ### update item_dict
        if project_id not in item_dict:
            item_dict.update({project_id: {}})
        if item_order not in item_dict[project_id]:
            item_dict[project_id].update({item_order: {}})
        if checked == 0:
            item_dict[project_id][item_order].update({'indent': indent,
                                                      'name': name,
                                                      'id': id,
                                                      'project_id': project_id})

def turn_dict_to_list(thedict): #only when indent <=5
    # thedict=item_dict[]
    list=thedict.keys()
    list.sort()
    theitemtree={}
    current_task_id_1st=0
    current_task_id_2st=0
    current_task_id_3st = 0
    current_task_id_4st = 0
    for order in list:
        try:
            indent=thedict[order]['indent']
            id=thedict[order]['id']
            if indent==1:
                theitemtree.update({id:{'-':'-'}})
                current_task_id_1st=id
            if indent==2:
                current_task_id_2st=id
                theitemtree[current_task_id_1st].update({id:{'-':'-'}})
            if indent==3:
                current_task_id_3st = id
                theitemtree[current_task_id_1st][current_task_id_2st].update({id:{'-':'-'}})
            if indent == 4:
                current_task_id_4st = id
                theitemtree[current_task_id_1st][current_task_id_2st][current_task_id_3st].update({id: {'-': '-'}})
            if indent == 5:
                theitemtree[current_task_id_1st][current_task_id_2st]\
                    [current_task_id_3st][current_task_id_4st].update({id: {'-': '-'}})
        except:
            pass
    tree = theitemtree
    list_of_lists = []

    def listbuilder(sub_tree, current_list):
        for key in sub_tree:
            if isinstance(sub_tree[key], dict):
                listbuilder(sub_tree[key], current_list + [key])
            else:
                list_of_lists.append(current_list + [key] + [sub_tree[key]])
    listbuilder(tree,[])

    return list_of_lists

def get_list_contains_id(id,lists):
    all_list_contains_id=[]
    for list in lists:
        if id in list:
            list= [x for x in list if x != '-']
            all_list_contains_id.append(list)
    return all_list_contains_id

def get_top_parent(id,parent_id):
    parent=parent_id[id]
    while True:
        try:
            parent=parent_id[parent]
            if parent==parent_id[parent]:
                break
        except:
            break
    return parent

def get_full_todo_for_pomotodo(id):
    global today_todo_name

    project_id = item_para_dict[id]['project_id'] # give id produce project_id
    thedict = item_dict[project_id] #give project id produce all items in this project
    dicttolists=turn_dict_to_list(thedict)
    thelist = get_list_contains_id(id, dicttolists) #turn project dict to lists which contains lists


    topparent = get_top_parent(project_id, parent_project_id) #top parent project
    toptag = '#' + project_name[topparent]
    thetodo = toptag

    if not project_id == topparent: #append most down sub project
        thetodo += ' ' + '#' + project_name[project_id]
    try:
        if not type(thelist[0])==type([1,2,3]):
            for id in thelist:
                thetodo += ' ' + item_para_dict[id]['name']
            return [thetodo]
        else:
            todo_samepart=thetodo #same parts is the project tags
            maxlen= len(max(thelist,key=len))

            for list in thelist:
                if len(list) ==maxlen:
                    todo=todo_samepart
                    checked=0
                    for id in list:
                        idname=item_para_dict[id]['name']
                        todo += ' | ' + idname
                        if item_para_dict[id]['checked']==1:
                            checked=1
                            break

                    if checked==0:
                        today_todo_name.update({id:todo})

    except Exception as e:
        print '\n'
        print '### error * '*10
        print str(e)
        print '### error * ' * 10
        print '\n'
