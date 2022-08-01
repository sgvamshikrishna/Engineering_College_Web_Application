import numpy as np
import mysql.connector
import simplejson as json
from flask import Flask, jsonify, render_template, request, make_response
from markupsafe import escape
from json import loads, dumps
from decimal import Decimal

from sympy import E


def default(obj):
    if isinstance(obj, Decimal):
        return json.JSONEncoder(f"{obj.normalize():f}")
    raise TypeError("Object of type '%s' is not JSON serializable" %
                    type(obj).__name__)


app = Flask(__name__)

cnx = mysql.connector.connect(user='root', password='Oracle@19',
                              host='127.0.0.1',
                              database='fdb_project')

cursor = cnx.cursor()


@app.route("/")
@app.route("/index.html")
def get_index():
    return render_template('index.html')


@app.route("/table/<tablename>")
def get_table_data(tablename):
    query = f"SELECT * from {escape(tablename)}"
    cursor.execute(query)
    data = json.loads(json.dumps(
        [dict(zip(cursor.column_names, row)) for row in cursor], default=default))
    return render_template('table.html', colnames=cursor.column_names, data=data)


@app.route("/table/update", methods=['POST'])
def update():
    try:
        json_data = request.get_json()
        table_name = json_data.get('tableName')
        column_names = json_data.get('data').get('columnNames')
        row_data = json_data.get('data').get('rowData')
        delete_query = f"delete from {table_name};"
        cursor.execute(delete_query)
        cnx.commit()
        for row in row_data:
            row_query = f"""insert into {table_name} ({', '.join(column_names)}) values ("{'", "'.join(row)}");"""
            print(row_query)
            cursor.execute(row_query)
            cnx.commit()
        return make_response(jsonify({"message": "Sucessfully Commited Data into Table"}), 200)
    except Exception as exception:
        return make_response(jsonify({"message": str(exception)}), 500)


app.run(host='0.0.0.0', port=80, debug=True)

