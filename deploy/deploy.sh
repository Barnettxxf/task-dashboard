#!/bin/bash

# Deployment script for Task Dashboard
# This script helps deploy the application by replacing placeholders with actual values

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required environment variables are set
check_env_vars() {
    local missing_vars=()
    
    [[ -z "$DOMAIN_NAME" ]] && missing_vars+=("DOMAIN_NAME")
    [[ -z "$SSL_CERT_PATH" ]] && missing_vars+=("SSL_CERT_PATH")
    [[ -z "$SSL_KEY_PATH" ]] && missing_vars+=("SSL_KEY_PATH")
    [[ -z "$APP_PATH" ]] && missing_vars+=("APP_PATH")
    [[ -z "$VENV_PATH" ]] && missing_vars+=("VENV_PATH")
    [[ -z "$SERVICE_USER" ]] && missing_vars+=("SERVICE_USER")
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        echo "Please set the following environment variables:"
        echo "  export DOMAIN_NAME=your-domain.com"
        echo "  export SSL_CERT_PATH=/path/to/certificate.crt"
        echo "  export SSL_KEY_PATH=/path/to/private.key"
        echo "  export APP_PATH=/path/to/task-dashboard"
        echo "  export VENV_PATH=/path/to/venv"
        echo "  export SERVICE_USER=www-data"
        exit 1
    fi
}

# Function to replace placeholders in a file
replace_placeholders() {
    local file=$1
    print_status "Updating placeholders in $file"
    
    # Replace domain name
    sed -i "s|your-domain.com|$DOMAIN_NAME|g" "$file"
    
    # Replace SSL certificate paths
    sed -i "s|/path/to/your/certificate.crt|$SSL_CERT_PATH|g" "$file"
    sed -i "s|/path/to/your/private.key|$SSL_KEY_PATH|g" "$file"
    
    # Replace application paths
    sed -i "s|/path/to/your/task-dashboard|$APP_PATH|g" "$file"
    sed -i "s|/path/to/your/venv|$VENV_PATH|g" "$file"
    
    # Replace service user
    sed -i "s|www-data|$SERVICE_USER|g" "$file"
    
    print_status "Updated $file with your configuration"
}

# Function to deploy nginx configuration
deploy_nginx() {
    print_status "Deploying nginx configuration..."
    
    # Copy nginx config to sites-available
    sudo cp nginx.conf /etc/nginx/sites-available/task-dashboard
    
    # Replace placeholders in the copied file
    sudo sed -i "s|your-domain.com|$DOMAIN_NAME|g" /etc/nginx/sites-available/task-dashboard
    sudo sed -i "s|/path/to/your/certificate.crt|$SSL_CERT_PATH|g" /etc/nginx/sites-available/task-dashboard
    sudo sed -i "s|/path/to/your/private.key|$SSL_KEY_PATH|g" /etc/nginx/sites-available/task-dashboard
    sudo sed -i "s|/path/to/your/task-dashboard|$APP_PATH|g" /etc/nginx/sites-available/task-dashboard
    
    # Create symbolic link if it doesn't exist
    if [ ! -L /etc/nginx/sites-enabled/task-dashboard ]; then
        sudo ln -s /etc/nginx/sites-available/task-dashboard /etc/nginx/sites-enabled/
        print_status "Created symbolic link for nginx site"
    fi
    
    # Test nginx configuration
    if sudo nginx -t; then
        sudo systemctl reload nginx
        print_status "Nginx configuration deployed and reloaded successfully"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
}

# Function to deploy systemd service
deploy_service() {
    print_status "Deploying systemd service..."
    
    # Copy service file
    sudo cp task-dashboard.service /etc/systemd/system/task-dashboard.service
    
    # Replace placeholders in the service file
    sudo sed -i "s|/path/to/your/task-dashboard|$APP_PATH|g" /etc/systemd/system/task-dashboard.service
    sudo sed -i "s|/path/to/your/venv|$VENV_PATH|g" /etc/systemd/system/task-dashboard.service
    sudo sed -i "s|www-data|$SERVICE_USER|g" /etc/systemd/system/task-dashboard.service
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable task-dashboard
    
    print_status "Systemd service deployed and enabled"
    echo "To start the service, run: sudo systemctl start task-dashboard"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [nginx|service|all]"
    echo ""
    echo "Commands:"
    echo "  nginx   - Deploy only nginx configuration"
    echo "  service - Deploy only systemd service"
    echo "  all     - Deploy both nginx and service (default)"
    echo ""
    echo "Required Environment Variables:"
    echo "  DOMAIN_NAME     - Your domain name (e.g., example.com)"
    echo "  SSL_CERT_PATH   - Path to SSL certificate file"
    echo "  SSL_KEY_PATH    - Path to SSL private key file"
    echo "  APP_PATH        - Path to task-dashboard application directory"
    echo "  VENV_PATH       - Path to Python virtual environment"
    echo "  SERVICE_USER    - User to run the service under"
    echo ""
    echo "Example:"
    echo "  export DOMAIN_NAME=example.com"
    echo "  export SSL_CERT_PATH=/etc/ssl/certs/example.com.crt"
    echo "  export SSL_KEY_PATH=/etc/ssl/private/example.com.key"
    echo "  export APP_PATH=/opt/task-dashboard"
    echo "  export VENV_PATH=/opt/task-dashboard/venv"
    echo "  export SERVICE_USER=www-data"
    echo "  $0 all"
}

# Main execution
main() {
    # Check if help is requested
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    # Check for required environment variables
    check_env_vars
    
    # Determine what to deploy
    local deploy_target=${1:-all}
    
    case $deploy_target in
        nginx)
            replace_placeholders "nginx.conf"
            deploy_nginx
            ;;
        service)
            replace_placeholders "task-dashboard.service"
            deploy_service
            ;;
        all)
            replace_placeholders "nginx.conf"
            replace_placeholders "task-dashboard.service"
            deploy_nginx
            deploy_service
            ;;
        *)
            print_error "Unknown command: $deploy_target"
            show_usage
            exit 1
            ;;
    esac
    
    print_status "Deployment completed successfully!"
    echo "Remember to start your service with: sudo systemctl start task-dashboard"
}

# Run main function with all arguments
main "$@"