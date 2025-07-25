import pytest
import json
from unittest.mock import Mock, patch
from app import app, build_query

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client"""
    with patch('app.client') as mock_client:
        yield mock_client

class TestHealthEndpoint:
    """Test cases for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint returns healthy status"""
        response = client.get('/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert 'USA Names API is running' in data['message']

class TestColumnsEndpoint:
    """Test cases for columns endpoint"""
    
    def test_get_columns(self, client):
        """Test columns endpoint returns correct column information"""
        response = client.get('/api/columns')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['columns']) == 4
        
        # Check column names
        column_names = [col['name'] for col in data['columns']]
        expected_names = ['gender', 'state', 'year', 'name']
        assert column_names == expected_names
        
        # Check column types
        for col in data['columns']:
            assert 'name' in col
            assert 'type' in col
            assert 'description' in col

class TestDataEndpoint:
    """Test cases for data endpoint"""
    
    def test_get_data_no_filters(self, client, mock_bigquery_client):
        """Test data endpoint with no filters"""
        # Mock query results
        mock_row1 = Mock()
        mock_row1.gender = 'M'
        mock_row1.state = 'CA'
        mock_row1.year = 1990
        mock_row1.name = 'John'
        
        mock_row2 = Mock()
        mock_row2.gender = 'F'
        mock_row2.state = 'NY'
        mock_row2.year = 1991
        mock_row2.name = 'Jane'
        
        mock_results = [mock_row1, mock_row2]
        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_results
        mock_bigquery_client.query.return_value = mock_query_job
        
        response = client.get('/api/data')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['count'] == 2
        assert len(data['data']) == 2
        
        # Check first record
        assert data['data'][0]['gender'] == 'M'
        assert data['data'][0]['state'] == 'CA'
        assert data['data'][0]['year'] == 1990
        assert data['data'][0]['name'] == 'John'
    
    def test_get_data_with_gender_filter(self, client, mock_bigquery_client):
        """Test data endpoint with gender filter"""
        mock_row = Mock()
        mock_row.gender = 'F'
        mock_row.state = 'CA'
        mock_row.year = 1990
        mock_row.name = 'Jane'
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        mock_bigquery_client.query.return_value = mock_query_job
        
        response = client.get('/api/data?gender=F')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['count'] == 1
        assert data['data'][0]['gender'] == 'F'
    
    def test_get_data_with_state_filter(self, client, mock_bigquery_client):
        """Test data endpoint with state filter"""
        mock_row = Mock()
        mock_row.gender = 'M'
        mock_row.state = 'NY'
        mock_row.year = 1990
        mock_row.name = 'John'
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        mock_bigquery_client.query.return_value = mock_query_job
        
        response = client.get('/api/data?state=NY')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['data'][0]['state'] == 'NY'
    
    def test_get_data_with_year_filter(self, client, mock_bigquery_client):
        """Test data endpoint with year filter"""
        mock_row = Mock()
        mock_row.gender = 'M'
        mock_row.state = 'CA'
        mock_row.year = 1990
        mock_row.name = 'John'
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        mock_bigquery_client.query.return_value = mock_query_job
        
        response = client.get('/api/data?year=1990')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['data'][0]['year'] == 1990
    
    def test_get_data_with_name_filter(self, client, mock_bigquery_client):
        """Test data endpoint with name filter"""
        mock_row = Mock()
        mock_row.gender = 'M'
        mock_row.state = 'CA'
        mock_row.year = 1990
        mock_row.name = 'John'
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        mock_bigquery_client.query.return_value = mock_query_job
        
        response = client.get('/api/data?name=John')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['data'][0]['name'] == 'John'
    
    def test_get_data_with_limit(self, client, mock_bigquery_client):
        """Test data endpoint with limit parameter"""
        mock_query_job = Mock()
        mock_query_job.result.return_value = []
        mock_bigquery_client.query.return_value = mock_query_job
        
        response = client.get('/api/data?limit=5')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['count'] == 0
    
    def test_get_data_with_multiple_filters(self, client, mock_bigquery_client):
        """Test data endpoint with multiple filters"""
        mock_row = Mock()
        mock_row.gender = 'F'
        mock_row.state = 'CA'
        mock_row.year = 1990
        mock_row.name = 'Jane'
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        mock_bigquery_client.query.return_value = mock_query_job
        
        response = client.get('/api/data?gender=F&state=CA&year=1990')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['data'][0]['gender'] == 'F'
        assert data['data'][0]['state'] == 'CA'
        assert data['data'][0]['year'] == 1990
    
    def test_get_data_bigquery_error(self, client, mock_bigquery_client):
        """Test data endpoint handles BigQuery errors"""
        mock_bigquery_client.query.side_effect = Exception("BigQuery error")
        
        response = client.get('/api/data')
        data = json.loads(response.data)
        
        assert response.status_code == 500
        assert data['status'] == 'error'
        assert 'BigQuery error' in data['message']

class TestBuildQueryFunction:
    """Test cases for build_query function"""
    
    def test_build_query_no_filters(self):
        """Test build_query with no filters"""
        query = build_query({})
        assert 'WHERE 1=1' in query
        assert 'ORDER BY year, state, name' in query
        assert 'LIMIT 100' in query
    
    def test_build_query_with_gender_filter(self):
        """Test build_query with gender filter"""
        query = build_query({'gender': 'M'})
        assert "gender = 'M'" in query
    
    def test_build_query_with_state_filter(self):
        """Test build_query with state filter"""
        query = build_query({'state': 'CA'})
        assert "state = 'CA'" in query
    
    def test_build_query_with_year_filter(self):
        """Test build_query with year filter"""
        query = build_query({'year': '1990'})
        assert 'year = 1990' in query
    
    def test_build_query_with_name_filter(self):
        """Test build_query with name filter"""
        query = build_query({'name': 'John'})
        assert "name LIKE '%John%'" in query
    
    def test_build_query_with_limit(self):
        """Test build_query with custom limit"""
        query = build_query({'limit': '5'})
        assert 'LIMIT 5' in query
    
    def test_build_query_with_multiple_filters(self):
        """Test build_query with multiple filters"""
        query = build_query({
            'gender': 'F',
            'state': 'NY',
            'year': '1990',
            'name': 'Jane',
            'limit': '10'
        })
        assert "gender = 'F'" in query
        assert "state = 'NY'" in query
        assert 'year = 1990' in query
        assert "name LIKE '%Jane%'" in query
        assert 'LIMIT 10' in query

if __name__ == '__main__':
    pytest.main([__file__]) 