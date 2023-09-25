from app import app, db
from flask import request, jsonify
from app.logic.generate_report import generate_report
from bson import ObjectId 

@app.route('/', methods=['GET'])
def get_nothin():


    return jsonify({'data': 'Hello World'})


@app.route('/trigger_report', methods=['GET'])
def trigger():
    data = generate_report(0)
    print('Report generation started')
    return jsonify({'report_id': data})

@app.route('/trigger_report/<count>', methods=['GET'])
def trigger_count(count):
    data = generate_report(count)
    print('Report generation started')
    return jsonify({'report_id': data})

@app.route('/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    data = db['reports'].find_one({'_id':ObjectId(report_id)})
    data["_id"] = str(data["_id"])
    return jsonify(data)

# Add other routes and MongoDB interactions as needed
