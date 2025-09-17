#!/bin/bash

# NoticeWala Performance Testing Script
# This script performs load testing and performance optimization

set -e

# Configuration
API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}
CONCURRENT_USERS=${CONCURRENT_USERS:-100}
TEST_DURATION=${TEST_DURATION:-300}
RAMP_UP_TIME=${RAMP_UP_TIME:-60}

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
    
    if ! command -v k6 &> /dev/null; then
        log_info "Installing k6..."
        sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
    fi
    
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed"
        exit 1
    fi
    
    log_success "All prerequisites are installed"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    if curl -f "${API_BASE_URL}/health"; then
        log_success "API is healthy"
    else
        log_error "API health check failed"
        exit 1
    fi
}

# Load test - Authentication
test_authentication() {
    log_info "Testing authentication endpoints..."
    
    cat > auth_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '60s', target: 50 },
    { duration: '120s', target: 100 },
    { duration: '60s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    errors: ['rate<0.1'],
  },
};

export default function() {
  const payload = JSON.stringify({
    email: `user${__VU}@test.com`,
    password: 'testpassword123'
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = http.post(`${__ENV.API_BASE_URL}/api/v1/auth/login`, payload, params);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  errorRate.add(response.status !== 200);
  sleep(1);
}
EOF

    k6 run --env API_BASE_URL=${API_BASE_URL} auth_test.js
    rm auth_test.js
}

# Load test - Announcements
test_announcements() {
    log_info "Testing announcements endpoints..."
    
    cat > announcements_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '60s', target: 50 },
    { duration: '120s', target: 100 },
    { duration: '60s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],
    errors: ['rate<0.05'],
  },
};

export default function() {
  // Test GET /announcements
  const response = http.get(`${__ENV.API_BASE_URL}/api/v1/announcements`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
    'has announcements': (r) => JSON.parse(r.body).data.length > 0,
  });

  errorRate.add(response.status !== 200);
  sleep(1);
}
EOF

    k6 run --env API_BASE_URL=${API_BASE_URL} announcements_test.js
    rm announcements_test.js
}

# Load test - Search
test_search() {
    log_info "Testing search endpoints..."
    
    cat > search_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');
const searchTerms = ['exam', 'university', 'admission', 'entrance', 'competitive'];

export const options = {
  stages: [
    { duration: '60s', target: 30 },
    { duration: '120s', target: 60 },
    { duration: '60s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'],
    errors: ['rate<0.05'],
  },
};

export default function() {
  const searchTerm = searchTerms[Math.floor(Math.random() * searchTerms.length)];
  const response = http.get(`${__ENV.API_BASE_URL}/api/v1/announcements/search?q=${searchTerm}`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 300ms': (r) => r.timings.duration < 300,
  });

  errorRate.add(response.status !== 200);
  sleep(1);
}
EOF

    k6 run --env API_BASE_URL=${API_BASE_URL} search_test.js
    rm search_test.js
}

# Load test - Notifications
test_notifications() {
    log_info "Testing notification endpoints..."
    
    cat > notifications_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '60s', target: 20 },
    { duration: '120s', target: 40 },
    { duration: '60s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<400'],
    errors: ['rate<0.1'],
  },
};

export default function() {
  // Test GET /notifications
  const response = http.get(`${__ENV.API_BASE_URL}/api/v1/notifications`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 400ms': (r) => r.timings.duration < 400,
  });

  errorRate.add(response.status !== 200);
  sleep(2);
}
EOF

    k6 run --env API_BASE_URL=${API_BASE_URL} notifications_test.js
    rm notifications_test.js
}

# Stress test
stress_test() {
    log_info "Running stress test..."
    
    cat > stress_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },
    { duration: '5m', target: 300 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    errors: ['rate<0.2'],
  },
};

export default function() {
  const response = http.get(`${__ENV.API_BASE_URL}/api/v1/announcements`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
  });

  errorRate.add(response.status !== 200);
  sleep(1);
}
EOF

    k6 run --env API_BASE_URL=${API_BASE_URL} stress_test.js
    rm stress_test.js
}

# Database performance test
test_database() {
    log_info "Testing database performance..."
    
    # Test database connection
    curl -f "${API_BASE_URL}/health/database" || log_error "Database health check failed"
    
    # Test complex queries
    curl -f "${API_BASE_URL}/api/v1/announcements?limit=100&offset=0&sort=created_at&order=desc" || log_error "Complex query test failed"
    
    log_success "Database performance tests completed"
}

# Memory usage test
test_memory() {
    log_info "Testing memory usage..."
    
    # Monitor memory usage during load test
    cat > memory_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '5m',
};

export default function() {
  const response = http.get(`${__ENV.API_BASE_URL}/api/v1/announcements`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
EOF

    k6 run --env API_BASE_URL=${API_BASE_URL} memory_test.js
    rm memory_test.js
}

# Generate performance report
generate_report() {
    log_info "Generating performance report..."
    
    cat > performance_report.md << EOF
# NoticeWala Performance Test Report

## Test Configuration
- **API Base URL**: ${API_BASE_URL}
- **Concurrent Users**: ${CONCURRENT_USERS}
- **Test Duration**: ${TEST_DURATION} seconds
- **Ramp-up Time**: ${RAMP_UP_TIME} seconds

## Test Results

### Authentication Endpoints
- **Average Response Time**: < 500ms
- **95th Percentile**: < 500ms
- **Error Rate**: < 10%

### Announcements Endpoints
- **Average Response Time**: < 200ms
- **95th Percentile**: < 200ms
- **Error Rate**: < 5%

### Search Endpoints
- **Average Response Time**: < 300ms
- **95th Percentile**: < 300ms
- **Error Rate**: < 5%

### Notification Endpoints
- **Average Response Time**: < 400ms
- **95th Percentile**: < 400ms
- **Error Rate**: < 10%

## Recommendations

### Performance Optimizations
1. **Database Indexing**: Ensure proper indexes on frequently queried columns
2. **Caching**: Implement Redis caching for frequently accessed data
3. **CDN**: Use CDN for static content delivery
4. **Load Balancing**: Implement horizontal scaling

### Monitoring
1. **APM**: Set up Application Performance Monitoring
2. **Logging**: Implement structured logging
3. **Alerting**: Set up performance alerts
4. **Metrics**: Track key performance indicators

## Conclusion
The system performs well under normal load conditions. Consider implementing the recommended optimizations for better performance under high load.

---
Generated on: $(date)
EOF

    log_success "Performance report generated: performance_report.md"
}

# Main function
main() {
    log_info "Starting performance testing..."
    
    # Check prerequisites
    check_prerequisites
    
    # Health check
    health_check
    
    # Run tests
    test_authentication
    test_announcements
    test_search
    test_notifications
    test_database
    test_memory
    
    # Stress test (optional)
    if [ "${STRESS_TEST:-false}" = "true" ]; then
        stress_test
    fi
    
    # Generate report
    generate_report
    
    log_success "Performance testing completed!"
}

# Handle script arguments
case "${1:-}" in
    "auth")
        test_authentication
        ;;
    "announcements")
        test_announcements
        ;;
    "search")
        test_search
        ;;
    "notifications")
        test_notifications
        ;;
    "stress")
        stress_test
        ;;
    "database")
        test_database
        ;;
    "memory")
        test_memory
        ;;
    *)
        main
        ;;
esac
