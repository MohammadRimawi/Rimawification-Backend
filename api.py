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
    if request.data:
        g.data = request.get_json()
    

@app.after_request
def after_request_func(response):
    
    if response.status_code >= 400 :
        g.transaction.rollback()
        res = response.get_json()
        if 'server message' in res:
            pprint(res['server message'])
        if 'response' in res and 'error' in res['response']:
            pprint(res['response']['error'])
    else:
        g.transaction.commit()
    g.conn.close()
    return response





# Description   :   Gets all widgets that are assigned to a page and thier readable information in a dict
# End-point     :   /api/get/all_page_widgets
# Methods       :   [ POST ]
# Takes         :   Nothing.
# Returns       :   widget_id, name ,page, order_by

@app.route("/api/get/tasks", methods=['POST','GET'])
def get_all_page_widgets():
    
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
            ''').dicts()
       
        response['response']['status'] = 200

    except Exception as e:
        response['response']['error'] = 'Server Error!\n"'+str(e)+'"' 
        response['response']['status'] = 500
    finally:
        return response,response['response']['status']



if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=5050,debug=True)