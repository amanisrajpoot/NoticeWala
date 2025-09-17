# NoticeWala API Documentation

## Overview

NoticeWala API provides endpoints for managing exam notifications, user subscriptions, and push notifications. The API follows RESTful principles and returns JSON responses.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### Login User
```http
POST /auth/login
```

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Announcements

#### Get Announcements
```http
GET /announcements?skip=0&limit=20&category=government&search=upsc
```

**Query Parameters:**
- `skip` (int): Number of items to skip (default: 0)
- `limit` (int): Number of items to return (default: 20, max: 100)
- `category` (string): Filter by category
- `search` (string): Search in title and content
- `sort_by` (string): Sort field (default: created_at)
- `sort_order` (string): Sort order - asc/desc (default: desc)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "UPSC Civil Services Exam 2025 Notification",
      "summary": "Union Public Service Commission announces Civil Services Exam 2025...",
      "content": "Full announcement content...",
      "source": {
        "id": "uuid",
        "name": "UPSC Official Website",
        "type": "government"
      },
      "source_url": "https://upsc.gov.in/notice/123",
      "publish_date": "2025-01-01T00:00:00Z",
      "exam_dates": [
        {
          "type": "exam_date",
          "start": "2025-06-01",
          "end": "2025-06-01",
          "note": "Preliminary Examination"
        }
      ],
      "application_deadline": "2025-03-15",
      "eligibility": "Bachelor's degree from recognized university",
      "location": {
        "country": "IN",
        "state": null,
        "city": null
      },
      "categories": ["government", "competitive"],
      "tags": ["upsc", "civil_services", "2025"],
      "language": "en",
      "priority_score": 0.85,
      "confidence": {
        "title": 0.98,
        "dates": 0.92,
        "eligibility": 0.87
      },
      "is_verified": true,
      "attachments": [],
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

#### Get Announcement by ID
```http
GET /announcements/{id}
```

#### Get Categories
```http
GET /announcements/categories/list
```

**Response:**
```json
{
  "categories": ["government", "competitive", "engineering", "medical", "scholarship"]
}
```

#### Get Sources
```http
GET /announcements/sources/list
```

### Subscriptions

#### Get User Subscriptions
```http
GET /subscriptions
Authorization: Bearer <token>
```

#### Create Subscription
```http
POST /subscriptions
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Government Exams",
  "filters": {
    "categories": ["government", "competitive"],
    "keywords": ["upsc", "ssc"],
    "locations": ["delhi", "mumbai"],
    "sources": ["source-id-1", "source-id-2"],
    "min_priority": 0.7
  },
  "notification_enabled": true,
  "priority_threshold": 70
}
```

#### Update Subscription
```http
PUT /subscriptions/{id}
Authorization: Bearer <token>
```

#### Delete Subscription
```http
DELETE /subscriptions/{id}
Authorization: Bearer <token>
```

### Notifications

#### Get User Notifications
```http
GET /notifications?skip=0&limit=20&status=sent
Authorization: Bearer <token>
```

#### Mark Notification as Read
```http
PUT /notifications/{id}/read
Authorization: Bearer <token>
```

#### Delete Notification
```http
DELETE /notifications/{id}
Authorization: Bearer <token>
```

#### Get Notification Settings
```http
GET /notifications/settings
Authorization: Bearer <token>
```

### Users

#### Get Current User Profile
```http
GET /users/me
Authorization: Bearer <token>
```

#### Update User Profile
```http
PUT /users/me
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "username": "newusername"
}
```

#### Register Push Token
```http
POST /users/push-token
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "token": "fcm-token-string",
  "platform": "android",
  "device_id": "device-unique-id",
  "app_version": "1.0.0",
  "os_version": "Android 13"
}
```

#### Unregister Push Token
```http
DELETE /users/push-token/{token}
Authorization: Bearer <token>
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message",
  "message": "Additional error context"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limiting

The API implements rate limiting:
- 100 requests per minute per IP address
- Authenticated users have higher limits

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks

For real-time updates, the API supports webhooks for:
- New announcements
- Updated announcements
- Subscription matches

Webhook endpoints receive POST requests with announcement data.

## SDKs and Libraries

Official SDKs are available for:
- React Native (JavaScript/TypeScript)
- Python
- Node.js

## Support

For API support and questions:
- Documentation: [GitHub Wiki](https://github.com/your-org/NoticeWala/wiki)
- Issues: [GitHub Issues](https://github.com/your-org/NoticeWala/issues)
- Email: api-support@noticewala.com
