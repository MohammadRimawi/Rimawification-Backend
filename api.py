from flask import Flask, render_template, request, session,make_response, g
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from pprint import pprint
from jsql import sql


app = Flask(__name__)


load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_HOST = os.getenv("DATABASE_HOST")

engine = create_engine(f'mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}')



@app.before_request
def before_request_func():
    g.conn = engine.connect()
    g.transaction = g.conn.begin()
  
    g.data = {}
    if request.method.lower() == "post" and request.data:
        g.data = request.get_json()
    

@app.after_request
def after_request_func(response):
    
    if response.status_code >= 400 :
        g.transaction.rollback()
        res = response.get_json()
        if 'response' in res and 'error' in res['response']:
            pprint(res['response']['error'])
    else:
        g.transaction.commit()
    g.conn.close()
    return response



######################################################################
#-----------------------------[ Tasks ]------------------------------#
######################################################################

###################################
#[ Create ]-----------------------#
###################################

# Description   :   Create new task
# End-point     :   /api/create/task
# Methods       :   [ POST ]
# Takes         :   [ title, description , color ]
# Returns       :   task_id.

@app.route("/api/create/task", methods=['POST'])
def create_task():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        response['data']['task_id'] = sql(g.conn,
        '''
            INSERT INTO 
                `tasks`(`title`, `description`, `color`) 
            VALUES 
                ( :title , :description , :color )
        ''',
        **g.data).lastrowid
       
        response['response']['status'] = 201

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']




# Description   :   Create new todo
# End-point     :   /api/create/todo
# Methods       :   [ POST ]
# Takes         :   [ `task_id`, `text` ]
# Returns       :   todo_id.

@app.route("/api/create/todo", methods=['POST'])
def create_todo():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        response['data']['todo_id'] = sql(g.conn,
        '''
            INSERT INTO 
                `todo`(`task_id`, `text`) 
            VALUES 
                ( :task_id , :text )
        ''',
        **g.data).lastrowid
       
        response['response']['status'] = 201

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']


###################################
#[ Get ]--------------------------#
###################################

# Description   :   Gets all tasks
# End-point     :   /api/get/tasks
# Methods       :   [ POST ]task
# Takes         :   Nothing.
# Returns       :   list of dicts of tasks [ task_id , title, description , color ]

@app.route("/api/get/tasks", methods=['POST','GET'])
@app.route("/api/get/tasks/<archived>", methods=['POST','GET'])

def all_tasks(archived=0):
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  


        response['data'] = sql(g.conn,
        '''
            SELECT 
                *
            FROM 
                tasks
            WHERE
                archived = :archived
            ''',archived=archived).dicts()
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']



#TODO to be changed to only return todos
# Description   :   Gets task
# End-point     :   /api/get/tasks
# Methods       :   [ POST ]
# Takes         :   task_id.
# Returns       :   dict of task and its todos [ task_id , title, description , color ]

@app.route("/api/get/task/<task_id>", methods=['POST','GET'])
@app.route("/api/get/task/<task_id>/<archived>", methods=['POST','GET'])
def get_task(task_id,archived = 0):
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        response['data'] = sql(g.conn,
        '''
            SELECT 
                *
            FROM 
               tasks
            WHERE
                task_id = :task_id
            
            ''',task_id=task_id).dict()

        response['data']['todos'] = sql(g.conn,
        '''
            SELECT 
                *
            FROM 
               todo
            WHERE
                task_id = :task_id
            AND
                archived = :archived
            
            ''',task_id=task_id,archived = archived).dicts()
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']


@app.route("/api/get/pinned_todos" , methods = ['POST','GET'])
def get_pinned_todos():
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        response['data'] = sql(g.conn,
        '''
            SELECT 
                *
            FROM 
               todo
            WHERE
                pinned = 1
            
            ''').dicts()

    
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']


###################################
#[ Update ]-----------------------#
###################################

#[ Task ]-------------------------#

# Description   :   Update task title
# End-point     :   /api/update/task/title
# Methods       :   [ POST ]
# Takes         :   [ task_id, title ]
# Returns       :   None.

@app.route("/api/update/task/title", methods=['POST'])
def update_task_title():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        sql(g.conn,
        '''
            UPDATE 
                `tasks` 
            SET 
                `title`= :title 
            WHERE 
                task_id = :task_id
        ''',
        **g.data)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']




# Description   :   Update task description
# End-point     :   /api/update/task/description
# Methods       :   [ POST ]
# Takes         :   [ task_id, description ]
# Returns       :   None.

@app.route("/api/update/task/description", methods=['POST'])
def update_task_description():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        sql(g.conn,
        '''
            UPDATE 
                `tasks` 
            SET 
                `description`= :description 
            WHERE 
                task_id = :task_id
        ''',
        **g.data)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']





# Description   :   Update task color
# End-point     :   /api/update/task/color
# Methods       :   [ POST ]
# Takes         :   [ task_id, color ]
# Returns       :   None.

@app.route("/api/update/task/color", methods=['POST'])
def update_task_color():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        sql(g.conn,
        '''
            UPDATE 
                `tasks` 
            SET 
                `color`= :color 
            WHERE 
                task_id = :task_id
        ''',
        **g.data)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']



# Description   :   Update task archived state
# End-point     :   /api/update/task/archived
# Methods       :   [ POST ]
# Takes         :   [ task_id, archived ]
# Returns       :   None.

@app.route("/api/update/task/archived", methods=['POST'])
def update_task_archived():
    
    response = {}
    response['data'] = {}
    response['response'] = {}
    # pprint(g.data)
    try:  
        sql(g.conn,
        '''
            UPDATE 
                `tasks` 
            SET 
                `archived`= :archived 
            WHERE 
                task_id = :task_id
        ''',
        **g.data)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']



#[ Todo ]-------------------------#

# Description   :   Update todo text
# End-point     :   /api/update/todo/text
# Methods       :   [ POST ]
# Takes         :   [ todo_id, text ]
# Returns       :   None.

@app.route("/api/update/todo/text", methods=['POST'])
def update_todo_text():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        sql(g.conn,
        '''
            UPDATE 
                `todo` 
            SET 
                `text`= :text 
            WHERE 
                todo_id = :todo_id
        ''',
        **g.data)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']


# Description   :   Update todo checked state
# End-point     :   /api/update/todo/checked
# Methods       :   [ POST ]
# Takes         :   [ todo_id, checked ]
# Returns       :   None.

@app.route("/api/update/todo/checked", methods=['POST'])
def update_todo_checked():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        sql(g.conn,
        '''
            UPDATE 
                `todo` 
            SET 
                `checked`= :checked 
            WHERE 
                todo_id = :todo_id
        ''',
        **g.data)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']



# Description   :   Update todo archived state
# End-point     :   /api/update/todo/archived
# Methods       :   [ POST ]
# Takes         :   [ todo_id, archived ]
# Returns       :   None.

@app.route("/api/update/todo/archived", methods=['POST'])
def update_todo_archived():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        sql(g.conn,
        '''
            UPDATE 
                `todo` 
            SET 
                `archived`= :archived 
            WHERE 
                todo_id = :todo_id
        ''',
        **g.data)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']


# Description   :   Update todo pinned state
# End-point     :   /api/update/todo/pinned
# Methods       :   [ POST ]
# Takes         :   [ todo_id, pinned ]
# Returns       :   None.

@app.route("/api/update/todo/pinned", methods=['POST'])
def update_todo_pinned():
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        sql(g.conn,
        '''
            UPDATE 
                `todo` 
            SET 
                `pinned`= :pinned 
            WHERE 
                todo_id = :todo_id
        ''',
        **g.data)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']



###################################
#[ Delete ]-----------------------#
###################################

# Description   :   Deletes task
# End-point     :   /api/delete/task
# Methods       :   [ DELETE ]
# Takes         :   task_id
# Returns       :   None.

@app.route("/api/delete/task/<task_id>", methods=['DELETE'])
def delete_task(task_id):
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:
        pprint(g.data)  
        sql(g.conn,
        '''
            DELETE FROM `tasks` WHERE task_id = :task_id
        ''',
        task_id = task_id)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']




# Description   :   Deletes todo
# End-point     :   /api/delete/todo
# Methods       :   [ DELETE ]
# Takes         :   todo_id
# Returns       :   None.

@app.route("/api/delete/todo/<todo_id>", methods=['DELETE'])
def delete_todo(todo_id):
    
    response = {}
    response['data'] = {}
    response['response'] = {}

    try:  
        sql(g.conn,
        '''
            DELETE FROM `todo` WHERE todo_id = :todo_id
        ''',
        todo_id = todo_id)
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']









# End-point     :   api/""/"" 
# Description   :   ""
# Methods       :   [ "" ]
# Takes         :   ""
# Returns       :   ""
######################################################################
#----------------------------[ Template ]----------------------------#
######################################################################

###################################
#[ Create ]-----------------------#
###################################

###################################
#[ Get ]--------------------------#
###################################

###################################
#[ Update ]-----------------------#
###################################

###################################
#[ Delete ]-----------------------#
###################################


if __name__ == '__main__':
    app.run(host = '127.0.0.1',port=5050,debug=False)
