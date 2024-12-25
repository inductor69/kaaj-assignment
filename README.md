# Florida Business Search

A full-stack web application that allows users to search and retrieve detailed information about businesses registered in Florida using the Sunbiz database.

## Features

- Real-time business search using Sunbiz.org
- Automatic data extraction and storage
- Detailed business information display including:
  - Business Name and Status
  - Filing Date
  - Registered Agent Information
  - Principal Officers/Directors
  - Annual Reports History
  - Document Links

## Tech Stack

### Frontend
- React with TypeScript
- Chakra UI for styling
- Axios for API calls

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- Playwright for web scraping
- PostgreSQL (Neon.tech hosted)

### Infrastructure
- Docker containerization
- Docker Compose for local development
- Neon.tech for database hosting

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.9+

### Installation

1. Clone the repository: 
```bash
git clone https://github.com/yourusername/florida-business-search.git
cd florida-business-search
```
2. Create environment files:
```bash
Frontend (.env)
REACT_APP_API_URL=http://localhost:8000/api
Backend (.env)
CORS_ORIGINS=http://localhost:3000
```
3. Start the application:
```bash
docker-compose up --build
```
## API Endpoints

### `GET /api/search/{business_name}`
Search for a business by name. Returns business details if found.

Response format:
```json
{
"id": 1,
"name": "ACME CARE & SERVICE, INC.",
"status": "Active",
"filing_date": "2003-10-21",
"principals": [...],
"registered_agent": {...}
}
```
```bash
Start all services
docker-compose up
Rebuild containers
docker-compose up --build
Stop all services
docker-compose down
```
