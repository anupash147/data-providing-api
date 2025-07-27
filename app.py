from flask import Flask, request, jsonify
from google.cloud import bigquery
import os
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize BigQuery client
GCP_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if GCP_CREDENTIALS and os.path.exists(GCP_CREDENTIALS):
    client = bigquery.Client.from_service_account_json(GCP_CREDENTIALS)
else:
    try:
        client = bigquery.Client()
    except Exception as e:
        logger.error("Google Cloud credentials not found. Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        raise e

def build_query(filters: Dict[str, str]) -> str:
    """Build SQL query with filters"""
    base_query = """
    SELECT gender, state, year, name
    FROM `learning-gcp-457917.dataform.usa_names_extract`
    WHERE 1=1
    """
    
    # Add filters
    if filters.get('gender'):
        base_query += f" AND gender = '{filters['gender']}'"
    if filters.get('state'):
        base_query += f" AND state = '{filters['state']}'"
    if filters.get('year'):
        base_query += f" AND year = {filters['year']}"
    if filters.get('name'):
        base_query += f" AND name LIKE '%{filters['name']}%'"
    
    base_query += " ORDER BY year, state, name"
    
    # Add limit if specified
    limit = filters.get('limit', 100)
    base_query += f" LIMIT {limit}"
    
    return base_query

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "USA Names API is running"})

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get USA names data with optional filters"""
    try:
        # Get query parameters
        filters = {
            'gender': request.args.get('gender'),
            'state': request.args.get('state'),
            'year': request.args.get('year'),
            'name': request.args.get('name'),
            'limit': request.args.get('limit', 100)
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Build and execute query
        query = build_query(filters)
        logger.info(f"Executing query: {query}")
        
        query_job = client.query(query)
        results = query_job.result()
        
        # Convert results to list of dictionaries
        data = []
        for row in results:
            data.append({
                'gender': row.gender,
                'state': row.state,
                'year': row.year,
                'name': row.name
            })
        
        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        })
        
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/columns', methods=['GET'])
def get_columns():
    """Get available columns for filtering"""
    return jsonify({
        "status": "success",
        "columns": [
            {"name": "gender", "type": "string", "description": "Gender of the person"},
            {"name": "state", "type": "string", "description": "State where the name was recorded"},
            {"name": "year", "type": "integer", "description": "Year of the record"},
            {"name": "name", "type": "string", "description": "Name of the person"}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 