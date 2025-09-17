#!/bin/bash

# NoticeWala Production Deployment Script
# Usage: ./scripts/deploy.sh [environment] [version]

set -e

# Configuration
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
PROJECT_NAME="noticewala"
REGISTRY="your-registry.com"
NAMESPACE="${PROJECT_NAME}-${ENVIRONMENT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed"
        exit 1
    fi
    
    log_success "All prerequisites are installed"
}

# Build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t ${REGISTRY}/${PROJECT_NAME}-backend:${VERSION} ./backend
    docker push ${REGISTRY}/${PROJECT_NAME}-backend:${VERSION}
    
    # Build mobile app image (if needed for server-side rendering)
    log_info "Building mobile image..."
    docker build -t ${REGISTRY}/${PROJECT_NAME}-mobile:${VERSION} ./mobile
    docker push ${REGISTRY}/${PROJECT_NAME}-mobile:${VERSION}
    
    log_success "Images built and pushed successfully"
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply configurations
    kubectl apply -f k8s/${ENVIRONMENT}/ -n ${NAMESPACE}
    
    # Update image tags
    kubectl set image deployment/backend backend=${REGISTRY}/${PROJECT_NAME}-backend:${VERSION} -n ${NAMESPACE}
    kubectl set image deployment/mobile mobile=${REGISTRY}/${PROJECT_NAME}-mobile:${VERSION} -n ${NAMESPACE}
    
    # Wait for rollout
    kubectl rollout status deployment/backend -n ${NAMESPACE}
    kubectl rollout status deployment/mobile -n ${NAMESPACE}
    
    log_success "Deployment completed successfully"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    kubectl run migration-${VERSION} \
        --image=${REGISTRY}/${PROJECT_NAME}-backend:${VERSION} \
        --restart=Never \
        --rm -i \
        --command -- alembic upgrade head \
        -n ${NAMESPACE}
    
    log_success "Database migrations completed"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Get service endpoint
    SERVICE_URL=$(kubectl get service backend -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$SERVICE_URL" ]; then
        SERVICE_URL=$(kubectl get service backend -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}')
    fi
    
    # Wait for service to be ready
    for i in {1..30}; do
        if curl -f http://${SERVICE_URL}:8000/health; then
            log_success "Health check passed"
            return 0
        fi
        log_info "Waiting for service to be ready... (${i}/30)"
        sleep 10
    done
    
    log_error "Health check failed"
    return 1
}

# Rollback deployment
rollback() {
    log_warning "Rolling back deployment..."
    
    kubectl rollout undo deployment/backend -n ${NAMESPACE}
    kubectl rollout undo deployment/mobile -n ${NAMESPACE}
    
    kubectl rollout status deployment/backend -n ${NAMESPACE}
    kubectl rollout status deployment/mobile -n ${NAMESPACE}
    
    log_success "Rollback completed"
}

# Main deployment function
main() {
    log_info "Starting deployment to ${ENVIRONMENT} environment with version ${VERSION}"
    
    # Check prerequisites
    check_prerequisites
    
    # Build and push images
    build_and_push_images
    
    # Deploy to Kubernetes
    deploy_to_kubernetes
    
    # Run migrations
    run_migrations
    
    # Health check
    if ! health_check; then
        log_error "Deployment failed health check. Rolling back..."
        rollback
        exit 1
    fi
    
    log_success "Deployment to ${ENVIRONMENT} completed successfully!"
    log_info "Application is available at: http://${SERVICE_URL}:8000"
}

# Handle script arguments
case "${1:-}" in
    "rollback")
        rollback
        ;;
    "health")
        health_check
        ;;
    *)
        main
        ;;
esac
