# USA Names Data API

A data pipeline and API service that extracts USA names data using GCP Dataform and provides a REST API for querying the data with filtering capabilities.

## Project Overview

This project consists of:
1. **GCP Dataform**: Creates and manages a cached view table with incremental data loading
2. **Python API**: Flask-based REST API that queries the data with column filters
3. **Docker Containerization**: Containerized API service
4. **CI/CD Pipeline**: Automated testing, building, and deployment to GCP

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   BigQuery      │    │   Dataform      │    │   Python API    │
│   Public Data   │───▶│   (Incremental  │───▶│   (Flask)       │
│                 │    │   Loading)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Docker        │
                                              │   Container     │
                                              └─────────────────┘
```

## Prerequisites

- Google Cloud Platform account
- BigQuery access
- Docker installed
- Python 3.9+
- Node.js (for Dataform)

## Setup Instructions

### 1. GCP Dataform Setup

```bash
# Install Dataform CLI
npm install -g @dataform/cli

# Initialize the project
make install
make create-dataform
make update-table
```

### 2. Local Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the API locally
export GOOGLE_APPLICATION_CREDENTIALS=/your/path/service-account-credentials.json
python app.py

# Run tests
pytest test_app.py -v
```

### 3. Docker Build

```bash
# Build the Docker image
docker build -t usa-names-api .

# Run the container
docker run -p 8080:8080 \
  -v ~/projects/bq-data-viewer-role.json:/app/gcp-key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-key.json \
  usa-names-api
docker run -p 8080:8080 usa-names-api
```

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API.

### Get Available Columns
```
GET /api/columns
```
Returns information about available columns for filtering.

### Get Data
```
GET /api/data?gender=M&state=CA&year=1990&name=John&limit=10
```

**Query Parameters:**
- `gender` (string): Filter by gender (M/F)
- `state` (string): Filter by state
- `year` (integer): Filter by year
- `name` (string): Filter by name (partial match)
- `limit` (integer): Limit number of results (default: 100)

**Response Format:**
```json
{
  "status": "success",
  "count": 5,
  "data": [
    {
      "gender": "M",
      "state": "CA",
      "year": 1990,
      "name": "John"
    }
  ]
}
```

## Dataform Configuration

The Dataform project is configured to:
- Extract data from `bigquery-public-data.usa_names.usa_1910_2013`
- Load data incrementally (10 rows at a time)
- Store results in `dataform_usa_names.usa_names_extract` table

### Key Files:
- `dataform.yaml`: Main configuration
- `definitions/usa_names_extract.sqlx`: Table definition with incremental loading

## CI/CD Pipeline

The GitHub Actions workflow (`/.github/workflows/ci-cd.yml`) includes:

1. **Testing**: Runs pytest with coverage
2. **Building**: Builds Docker image
3. **Pushing**: Pushes to Google Container Registry
4. **Deploying**: Deploys to Cloud Run

### Required Secrets:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Service account key for GCP authentication

## Makefile Commands

```bash
make help          # Show available commands
make install       # Install dependencies
make check-dataform # Check if Dataform project exists
make create-dataform # Create Dataform project if needed
make update-table  # Update the data table
make deploy        # Full deployment process
make clean         # Clean build artifacts
```

## Testing

The test suite covers:
- Health check endpoint
- Column information endpoint
- Data filtering with various parameters
- Error handling
- Query building logic

Run tests with:
```bash
pytest test_app.py -v --cov=app
```

## Deployment

### Local Docker
```bash
docker build -t usa-names-api .
docker run -p 8080:8080 usa-names-api
```

### GCP Cloud Run
The CI/CD pipeline automatically deploys to Cloud Run when changes are pushed to the main branch.

## Environment Variables

- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `PORT`: API port (default: 8080)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. 