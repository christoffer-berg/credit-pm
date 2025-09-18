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
- **AI**: OpenAI API, OpenRouter, LightGBM, Prophet
- **Export**: python-docx, reportlab

## Quick Start (Docker)

1. **Clone and setup environment**:
   ```bash
   git clone <your-repo-url>
   cd Credit-PM
   cp .env.example .env
   ```

2. **Configure environment variables** in `.env`:
   - Add your Supabase URL and keys
   - Add OpenAI API key
   - Add other API keys as needed

3. **Setup Supabase database**:
   - Go to your [Supabase Dashboard](https://supabase.com/dashboard)
   - Navigate to SQL Editor
   - Run the SQL from `database/supabase_financial_migration.sql`

4. **Start the application**:
   ```bash
   docker-compose up -d
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Deployment

### Backend Deployment (Railway)
1. Connect your GitHub repository to Railway
2. Set the following environment variables in Railway:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `OPENAI_API_KEY`
   - `BOLAGSVERKET_API_KEY`
   - `OPENROUTER_API_KEY`
   - `OPENROUTER_URL`

### Frontend Deployment (Netlify)
1. Connect your GitHub repository to Netlify
2. Set build settings:
   - Build command: `npm run build`
   - Publish directory: `out`
   - Base directory: `frontend`
3. Set environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL` (your Railway backend URL)

## Project Structure

```
credit-pm/
├── frontend/              # Next.js React application
│   ├── src/              # Source code
│   ├── pages/            # Pages Router pages
│   ├── public/           # Static assets
│   ├── Dockerfile        # Production Docker image
│   ├── Dockerfile.dev    # Development Docker image
│   └── next.config.mjs   # Next.js configuration
├── backend/              # FastAPI Python service
│   ├── api/              # API routes
│   ├── core/             # Core configuration
│   ├── services/         # Business logic
│   ├── Dockerfile        # Production Docker image
│   ├── Dockerfile.dev    # Development Docker image
│   └── requirements.txt  # Python dependencies
├── database/             # Database schemas and migrations
│   ├── init.sql          # Initial schema
│   └── supabase_financial_migration.sql  # Financial tables
├── docker-compose.yml    # Local development environment
├── railway.json          # Railway deployment config
├── netlify.toml          # Netlify deployment config
├── Procfile              # Railway process file
└── README.md
```

## Key Features

### 🏢 Company Analysis
- **Company Data Integration**: Automatic fetching from Bolagsverket API
- **Financial Data**: Integration with allabolag.se for financial statements
- **Document Processing**: PDF parsing for annual reports

### 🤖 AI-Powered Generation
- **Business Descriptions**: AI-generated company summaries
- **Market Analysis**: Automated industry and competitor analysis
- **Financial Forecasting**: 5-year financial projections using ML models
- **Credit Assessment**: Automated risk analysis and recommendations

### 📊 Financial Analysis
- **Complete Financial Overview**: Income statement, balance sheet, cash flow
- **Ratio Analysis**: Key financial ratios and benchmarking
- **Trend Analysis**: Historical performance tracking
- **Projection Models**: Prophet and LightGBM-based forecasting

### 📝 Document Management
- **Interactive Editing**: Inline editing with auto-save
- **Version Control**: Track changes and modifications
- **Export Options**: Word and PDF document generation
- **Audit Trail**: Complete logging of AI outputs and user modifications

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | ✅ |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | ✅ |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | ✅ |
| `OPENAI_API_KEY` | OpenAI API key | ✅ |
| `OPENROUTER_API_KEY` | OpenRouter API key | ✅ |
| `BOLAGSVERKET_API_KEY` | Bolagsverket API key | ⚠️ Optional |
| `NEXT_PUBLIC_API_URL` | Backend URL (production only) | ⚠️ Production |

## API Endpoints

### Core Functionality
- `GET /api/v1/companies` - List companies
- `POST /api/v1/companies` - Create company
- `GET /api/v1/cases` - List credit memo cases
- `POST /api/v1/cases` - Create new case

### Financial Analysis
- `GET /api/v1/financials/companies/{id}/overview` - Complete financial overview
- `POST /api/v1/financials/companies/{id}/statements` - Create financial statements
- `POST /api/v1/financials/companies/{id}/projections` - Generate 5-year projections
- `POST /api/v1/financials/companies/{id}/analyze` - AI financial analysis

### Document Processing
- `POST /api/v1/financials/companies/{id}/upload-pdf` - Upload annual report PDFs
- `GET /api/v1/financials/companies/{id}/allabolag` - Fetch from allabolag.se

## Troubleshooting

### Docker Issues
- **Port conflicts**: Make sure ports 3000 and 8000 are available
- **Build failures**: Run `docker-compose build --no-cache` to rebuild images
- **Permission issues**: Check Docker daemon is running and has proper permissions

### Database Issues
- **Connection errors**: Verify Supabase credentials in `.env`
- **Missing tables**: Run the Supabase migration SQL scripts
- **RLS policies**: Ensure proper Row Level Security policies are in place

### Deployment Issues
- **Railway build failures**: Check environment variables and build logs
- **Netlify build failures**: Ensure Node.js version is set to 20
- **API connectivity**: Verify CORS settings and API URLs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test locally with Docker
4. Submit a pull request

## License

MIT License - see LICENSE file for details