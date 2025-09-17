#!/bin/bash

# NoticeWala Production Setup Script
# This script sets up the production environment

set -e

# Configuration
PROJECT_NAME="noticewala"
ENVIRONMENT="production"
REGISTRY="your-registry.com"

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

# Install required tools
install_tools() {
    log_info "Installing required tools..."
    
    # Install kubectl
    if ! command -v kubectl &> /dev/null; then
        log_info "Installing kubectl..."
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl
        sudo mv kubectl /usr/local/bin/
    fi
    
    # Install helm
    if ! command -v helm &> /dev/null; then
        log_info "Installing Helm..."
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi
    
    # Install docker
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        sudo usermod -aG docker $USER
    fi
    
    log_success "All tools installed successfully"
}

# Setup Kubernetes cluster
setup_kubernetes() {
    log_info "Setting up Kubernetes cluster..."
    
    # Create cluster using kind (for local development)
    if ! command -v kind &> /dev/null; then
        log_info "Installing kind..."
        curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
        chmod +x ./kind
        sudo mv ./kind /usr/local/bin/kind
    fi
    
    # Create cluster
    kind create cluster --name ${PROJECT_NAME}-${ENVIRONMENT}
    
    # Setup kubectl context
    kubectl cluster-info --context kind-${PROJECT_NAME}-${ENVIRONMENT}
    
    log_success "Kubernetes cluster setup completed"
}

# Setup monitoring stack
setup_monitoring() {
    log_info "Setting up monitoring stack..."
    
    # Add Prometheus Helm repository
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # Install Prometheus
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --values monitoring/prometheus-values.yaml
    
    # Install Grafana
    helm install grafana grafana/grafana \
        --namespace monitoring \
        --set adminPassword=admin123 \
        --set service.type=LoadBalancer
    
    log_success "Monitoring stack setup completed"
}

# Setup logging stack
setup_logging() {
    log_info "Setting up logging stack..."
    
    # Add Elasticsearch Helm repository
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    # Install Elasticsearch
    helm install elasticsearch elastic/elasticsearch \
        --namespace logging \
        --create-namespace \
        --values logging/elasticsearch-values.yaml
    
    # Install Kibana
    helm install kibana elastic/kibana \
        --namespace logging \
        --set service.type=LoadBalancer
    
    # Install Logstash
    helm install logstash elastic/logstash \
        --namespace logging \
        --values logging/logstash-values.yaml
    
    log_success "Logging stack setup completed"
}

# Setup ingress
setup_ingress() {
    log_info "Setting up ingress controller..."
    
    # Add NGINX Ingress Helm repository
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # Install NGINX Ingress Controller
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer
    
    log_success "Ingress controller setup completed"
}

# Setup SSL certificates
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    # Add cert-manager Helm repository
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    # Install cert-manager
    helm install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --version v1.13.0 \
        --set installCRDs=true
    
    # Wait for cert-manager to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
    
    # Apply Let's Encrypt ClusterIssuer
    kubectl apply -f k8s/cert-manager/cluster-issuer.yaml
    
    log_success "SSL certificates setup completed"
}

# Setup backup
setup_backup() {
    log_info "Setting up backup system..."
    
    # Install Velero for backup
    if ! command -v velero &> /dev/null; then
        log_info "Installing Velero..."
        wget https://github.com/vmware-tanzu/velero/releases/download/v1.11.1/velero-v1.11.1-linux-amd64.tar.gz
        tar -xvf velero-v1.11.1-linux-amd64.tar.gz
        sudo mv velero-v1.11.1-linux-amd64/velero /usr/local/bin/
    fi
    
    # Setup Velero (requires cloud provider configuration)
    log_warning "Velero setup requires cloud provider configuration"
    log_info "Please configure your cloud provider credentials and run:"
    log_info "velero install --provider <provider> --bucket <bucket> --secret-file <credentials>"
    
    log_success "Backup system setup completed"
}

# Main setup function
main() {
    log_info "Starting production environment setup..."
    
    # Install tools
    install_tools
    
    # Setup Kubernetes
    setup_kubernetes
    
    # Setup monitoring
    setup_monitoring
    
    # Setup logging
    setup_logging
    
    # Setup ingress
    setup_ingress
    
    # Setup SSL
    setup_ssl
    
    # Setup backup
    setup_backup
    
    log_success "Production environment setup completed successfully!"
    log_info "You can now deploy the application using: ./scripts/deploy.sh production"
}

# Handle script arguments
case "${1:-}" in
    "tools")
        install_tools
        ;;
    "kubernetes")
        setup_kubernetes
        ;;
    "monitoring")
        setup_monitoring
        ;;
    "logging")
        setup_logging
        ;;
    "ingress")
        setup_ingress
        ;;
    "ssl")
        setup_ssl
        ;;
    "backup")
        setup_backup
        ;;
    *)
        main
        ;;
esac
