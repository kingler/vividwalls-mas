#!/bin/bash

# VividWalls n8n Workflow Deployment Script
# This script uploads the VividWalls workflows to your n8n instance

set -e

# Configuration
N8N_BASE_URL="https://n8n.vividwalls.blog"
N8N_API_KEY="REDACTED_JWT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if n8n is accessible
check_n8n_connection() {
    print_status "Checking n8n connection..."
    
    if curl -s -f -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE_URL/api/v1/workflows" > /dev/null; then
        print_success "n8n connection successful"
        return 0
    else
        print_error "Failed to connect to n8n instance at $N8N_BASE_URL"
        print_error "Please check your n8n instance is running and API key is correct"
        return 1
    fi
}

# Function to upload a workflow
upload_workflow() {
    local workflow_file="$1"
    local workflow_name=$(basename "$workflow_file" .json)
    
    print_status "Uploading workflow: $workflow_name"
    
    if [ ! -f "$workflow_file" ]; then
        print_error "Workflow file not found: $workflow_file"
        return 1
    fi
    
    # Read the workflow JSON
    local workflow_data=$(cat "$workflow_file")
    
    # Upload the workflow
    local response=$(curl -s -w "%{http_code}" -o /tmp/n8n_response.json \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -d "$workflow_data" \
        "$N8N_BASE_URL/api/v1/workflows")
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        local workflow_id=$(cat /tmp/n8n_response.json | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        print_success "Workflow uploaded successfully: $workflow_name (ID: $workflow_id)"
        return 0
    else
        print_error "Failed to upload workflow: $workflow_name (HTTP: $http_code)"
        if [ -f /tmp/n8n_response.json ]; then
            print_error "Response: $(cat /tmp/n8n_response.json)"
        fi
        return 1
    fi
}

# Function to activate a workflow
activate_workflow() {
    local workflow_id="$1"
    local workflow_name="$2"
    
    print_status "Activating workflow: $workflow_name"
    
    local response=$(curl -s -w "%{http_code}" -o /tmp/n8n_activate_response.json \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        "$N8N_BASE_URL/api/v1/workflows/$workflow_id/activate")
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        print_success "Workflow activated: $workflow_name"
        return 0
    else
        print_warning "Failed to activate workflow: $workflow_name (HTTP: $http_code)"
        return 1
    fi
}

# Main deployment function
deploy_workflows() {
    print_status "Starting VividWalls workflow deployment..."
    
    # Check n8n connection first
    if ! check_n8n_connection; then
        exit 1
    fi
    
    # Define workflows to deploy
    local workflows=(
        "n8n/workflows/VividWalls-Test-Database-Connection.json"
        "n8n/workflows/VividWalls-Database-Integration-Workflow.json"
        "n8n/workflows/VividWalls-Prompt-Chain-Image-Retrieval.json"
    )
    
    local uploaded_workflows=()
    local failed_workflows=()
    
    # Upload each workflow
    for workflow_file in "${workflows[@]}"; do
        if upload_workflow "$workflow_file"; then
            uploaded_workflows+=("$workflow_file")
        else
            failed_workflows+=("$workflow_file")
        fi
    done
    
    # Summary
    echo
    print_status "Deployment Summary:"
    echo "  Successfully uploaded: ${#uploaded_workflows[@]} workflows"
    echo "  Failed uploads: ${#failed_workflows[@]} workflows"
    
    if [ ${#uploaded_workflows[@]} -gt 0 ]; then
        echo
        print_success "Successfully uploaded workflows:"
        for workflow in "${uploaded_workflows[@]}"; do
            echo "  - $(basename "$workflow" .json)"
        done
    fi
    
    if [ ${#failed_workflows[@]} -gt 0 ]; then
        echo
        print_error "Failed to upload workflows:"
        for workflow in "${failed_workflows[@]}"; do
            echo "  - $(basename "$workflow" .json)"
        done
    fi
    
    echo
    print_status "Next steps:"
    echo "1. Check your n8n instance at $N8N_BASE_URL"
    echo "2. Verify database credentials are configured"
    echo "3. Test the workflows using the provided curl commands"
    echo "4. Review the VIVIDWALLS_PROMPT_CHAIN_IMPLEMENTATION.md guide"
}

# Function to test database connection
test_database_connection() {
    print_status "Testing database connection..."
    
    local response=$(curl -s -w "%{http_code}" -o /tmp/db_test_response.json \
        -X POST \
        -H "Content-Type: application/json" \
        "$N8N_BASE_URL/webhook/test-db-connection")
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        print_success "Database connection test successful"
        echo "Response: $(cat /tmp/db_test_response.json | head -c 200)..."
        return 0
    else
        print_error "Database connection test failed (HTTP: $http_code)"
        if [ -f /tmp/db_test_response.json ]; then
            print_error "Response: $(cat /tmp/db_test_response.json)"
        fi
        return 1
    fi
}

# Function to test prompt chain
test_prompt_chain() {
    print_status "Testing prompt chain workflow..."
    
    local test_data='{
        "inquiry": "I need calming blue artwork for my bedroom",
        "roomType": "bedroom",
        "moodPreference": "calming",
        "colorPreferences": ["blue"],
        "sessionId": "test_session_deployment"
    }'
    
    local response=$(curl -s -w "%{http_code}" -o /tmp/prompt_test_response.json \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$test_data" \
        "$N8N_BASE_URL/webhook/prompt-chain-retrieval")
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        print_success "Prompt chain test successful"
        echo "Response preview: $(cat /tmp/prompt_test_response.json | head -c 300)..."
        return 0
    else
        print_error "Prompt chain test failed (HTTP: $http_code)"
        if [ -f /tmp/prompt_test_response.json ]; then
            print_error "Response: $(cat /tmp/prompt_test_response.json)"
        fi
        return 1
    fi
}

# Command line interface
case "${1:-deploy}" in
    "deploy")
        deploy_workflows
        ;;
    "test-db")
        test_database_connection
        ;;
    "test-prompt")
        test_prompt_chain
        ;;
    "test-all")
        test_database_connection
        echo
        test_prompt_chain
        ;;
    "help")
        echo "VividWalls n8n Workflow Deployment Script"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  deploy      Deploy all workflows to n8n (default)"
        echo "  test-db     Test database connection"
        echo "  test-prompt Test prompt chain workflow"
        echo "  test-all    Run all tests"
        echo "  help        Show this help message"
        echo
        echo "Configuration:"
        echo "  N8N_BASE_URL: $N8N_BASE_URL"
        echo "  API Key: ${N8N_API_KEY:0:20}..."
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

# Cleanup
rm -f /tmp/n8n_response.json /tmp/n8n_activate_response.json /tmp/db_test_response.json /tmp/prompt_test_response.json 