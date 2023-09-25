from app import app, db
from flask import request, jsonify


@app.route('/trigger_report', methods=['GET'])
def get_users():
    data = list(db.store_zones.find())  # Retrieve all documents from the collection
    
    # Convert ObjectId to string for each document (if needed)
    for document in data:
        document['_id'] = str(document['_id'])

    return jsonify({'data': data})