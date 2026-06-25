# API Specification

## Base URL
```
Production: https://api.interview-pro.com/v1
Development: http://localhost:8000/v1
```

## Authentication
All endpoints require JWT bearer token unless marked as public.

## Endpoints

### Auth
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Invalidate tokens

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `DELETE /users/me` - Delete account

### Interviews
- `GET /interviews` - List user's interviews
- `POST /interviews` - Start new interview
- `GET /interviews/{id}` - Get interview details
- `DELETE /interviews/{id}` - Delete interview

### Analysis
- `POST /analysis/{id}/start` - Start analysis
- `GET /analysis/{id}/status` - Get analysis status
- `GET /analysis/{id}/results` - Get analysis results

### Reports
- `GET /reports` - List user's reports
- `GET /reports/{id}` - Get report details
- `GET /reports/{id}/export` - Export report (PDF)
