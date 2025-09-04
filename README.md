# Credit PM Generator

Automated credit memo generation service for banking professionals.

## Overview

This system automates the creation of credit memos for companies by combining:
- Public company data (Bolagsverket API)
- Commercial risk data (UC/D&B integration)
- Macro data (e.g., STIBOR)
- AI-powered text generation and financial forecasting

## Tech Stack

- **Frontend**: Next.js with TypeScript, shadcn/ui, Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: Supabase (PostgreSQL with pgvector)
- **AI**: OpenAI API, LightGBM, Prophet
- **Export**: python-docx, reportlab

## Quick Start

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Fill in your API keys and database credentials in `.env`

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Local Development
Each service can be developed independently:

```bash
# Frontend only
cd frontend && npm run dev

# Backend only  
cd backend && python -m uvicorn main:app --reload

# Database only
docker-compose up db
```

## Project Structure

```
credit-pm/
├── frontend/           # Next.js React application
├── backend/            # FastAPI Python service
├── database/           # Database schemas and migrations
├── docker-compose.yml  # Local development environment
└── README.md
```

## Features

- **Company Data Integration**: Automatic fetching from Bolagsverket API
- **AI-Powered Analysis**: Generate business descriptions, market analysis, and financial forecasts
- **Interactive Editing**: Inline editing with auto-save and version control
- **Document Export**: Export to Word and PDF formats
- **Audit Trail**: Complete logging of AI outputs and user modifications