# Makefile for USA Names Data API
# Dataform project management and deployment

.PHONY: help install check-gcp-auth check-dataform create-dataform compile run update-table deploy clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install        - Install dependencies"
	@echo "  check-gcp-auth - Check GCP project and authentication"
	@echo "  check-dataform - Check local Dataform files (and optionally GCP repo)"
	@echo "  create-dataform - Ensure local Dataform files (and optionally GCP repo) exist"
	@echo "  compile        - Compile Dataform project using open-source CLI"
	@echo "  run            - Run Dataform workflow using open-source CLI"
	@echo "  update-table   - Compile and run Dataform workflow"
	@echo "  deploy         - Full deployment process"
	@echo "  clean          - Clean build artifacts"

# Install dependencies
install:
	npm install
	@echo "Dependencies installed successfully"

# Check GCP project and authentication
check-gcp-auth:
	@if [ -z "$$GOOGLE_CLOUD_PROJECT" ]; then \
		echo "[ERROR] GOOGLE_CLOUD_PROJECT environment variable is not set."; \
		echo "Please set it with: export GOOGLE_CLOUD_PROJECT=your-gcp-project-id"; \
		exit 1; \
	fi
	@CURRENT_PROJECT=$$(gcloud config get-value project 2>/dev/null); \
	if [ "$$CURRENT_PROJECT" != "$$GOOGLE_CLOUD_PROJECT" ]; then \
		echo "[ERROR] gcloud is not authenticated to the correct project."; \
		echo "Current gcloud project: $$CURRENT_PROJECT"; \
		echo "Expected: $$GOOGLE_CLOUD_PROJECT"; \
		echo "Run: gcloud config set project $$GOOGLE_CLOUD_PROJECT"; \
		exit 1; \
	fi
	@AUTH_COUNT=$$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | wc -l); \
	if [ "$$AUTH_COUNT" -eq 0 ]; then \
		echo "[ERROR] No active gcloud authentication found. Run: gcloud auth login"; \
		exit 1; \
	fi
	@echo "[OK] GOOGLE_CLOUD_PROJECT is set and gcloud is authenticated."

# Check local Dataform files (and optionally GCP repo)
check-dataform: check-gcp-auth
	@echo "Checking if Dataform project exists locally..."
	@if [ -f "dataform.json" ] && [ -d "definitions" ]; then \
		echo "Local Dataform project files exist."; \
	else \
		echo "[ERROR] Local Dataform project files not found. Run 'make init-dataform' to initialize."; \
		exit 1; \
	fi
	# Optional: Check for GCP Dataform repository (uncomment if needed)
	# @REPO_NAME=usa-names-data-api; \
	# REPO_EXISTS=$$(gcloud alpha dataform repositories list --location=us-central1 --project=$$GOOGLE_CLOUD_PROJECT --format="value(name)" | grep "$$REPO_NAME" || true); \
	# if [ -z "$$REPO_EXISTS" ]; then \
	# 	echo "[WARN] Dataform repository '$$REPO_NAME' does not exist in project '$$GOOGLE_CLOUD_PROJECT' (location: us-central1)."; \
	# else \
	# 	echo "[OK] Dataform repository '$$REPO_NAME' exists in GCP."; \
	# fi

# Initialize Dataform project if missing
defaultDatabase = $(GOOGLE_CLOUD_PROJECT)
init-dataform:
																																																																																	npx dataform init bigquery --default-database=$(GOOGLE_CLOUD_PROJECT) --default-location=us-central1
	@echo "Dataform project initialized. Please update dataform.json with your project details if needed."

# Ensure local Dataform files (and optionally GCP repo) exist
create-dataform: check-gcp-auth check-dataform
	@echo "Ensuring local Dataform files exist..."
	@if [ ! -f "dataform.json" ]; then \
		echo "Creating dataform.json..."; \
		echo '{\n  "warehouse": "bigquery",\n  "defaultSchema": "dataform_usa_names",\n  "defaultDatabase": "'$$GOOGLE_CLOUD_PROJECT'",\n  "assertionsSchema": "dataform_assertions",\n  "projectConfig": {},\n  "vars": {"dataset_name": "usa_names_data"}\n}' > dataform.json; \
	fi
	@if [ ! -d "definitions" ]; then \
		mkdir -p definitions; \
		echo "Created definitions directory"; \
	fi
	@echo "Local Dataform files are ready."
	# Optional: Create GCP Dataform repository (uncomment if needed)
	# @REPO_NAME=usa-names-data-api; \
	# REPO_EXISTS=$$(gcloud alpha dataform repositories list --location=us-central1 --project=$$GOOGLE_CLOUD_PROJECT --format="value(name)" | grep "$$REPO_NAME" || true); \
	# if [ -z "$$REPO_EXISTS" ]; then \
	# 	echo "Creating Dataform repository '$$REPO_NAME' in project '$$GOOGLE_CLOUD_PROJECT' (location: us-central1)..."; \
	# 	gcloud alpha dataform repositories create $$REPO_NAME --location=us-central1 --project=$$GOOGLE_CLOUD_PROJECT; \
	# else \
	# 	echo "[OK] Dataform repository '$$REPO_NAME' already exists in GCP."; \
	# fi

# Create a zip archive of the Dataform project for Cloud Dataform upload
zip-dataform:
	@echo "Creating dataform.zip archive for Cloud Dataform..."
	zip -r dataform.zip dataform.json definitions > /dev/null
	@echo "dataform.zip created."

# Compile Dataform project using open-source CLI and create zip for Cloud Dataform
compile: check-gcp-auth check-dataform zip-dataform
	@echo "Compiling Dataform project..."
	npx dataform compile

# Run Dataform workflow using open-source CLI
run: check-gcp-auth check-dataform
	@echo "Running Dataform workflow..."
	npx dataform run

# Compile and run Dataform workflow
update-table: compile run
	@echo "Table updated using Dataform CLI."

# Full deployment process
deploy: install create-dataform update-table
	@echo "Deployment completed successfully"

# Clean build artifacts
clean:
	rm -rf node_modules
	rm -rf .dataform
	@echo "Clean completed" 