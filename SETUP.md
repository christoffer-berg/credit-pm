# Credit PM Generator - Setup Guide

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Supabase account
- OpenAI API key (optional, for AI features)

## Quick Start

1. **Clone and Setup Environment**
   ```bash
   git clone <your-repo-url>
   cd Credit-PM
   cp .env.example .env
   ```

2. **Configure Environment Variables**
   Edit `.env` file with your credentials:
   ```bash
   # Supabase
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-key

   # AI Services
   OPENAI_API_KEY=your-openai-key

   # External APIs
   BOLAGSVERKET_API_KEY=your-bolagsverket-key
   ```

3. **Start All Services**
   ```bash
   docker-compose up -d
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Supabase Setup

1. Create a new Supabase project
2. Run the database initialization script:
   ```sql
   -- Copy and paste the content from database/init.sql
   ```
3. Enable Row Level Security (RLS) policies
4. Create your first user account

## Development Setup

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

### Database Development
```bash
docker-compose up db -d
```

## Configuration Guide

### 1. Supabase Configuration
- Create project in Supabase dashboard
- Copy URL and keys to `.env`
- Run database schema from `database/init.sql`
- Configure authentication settings

### 2. OpenAI Configuration
- Create OpenAI account
- Generate API key
- Add to `.env` as `OPENAI_API_KEY`

### 3. Bolagsverket API (Optional)
- Register for Bolagsverket API access
- Add key to `.env` as `BOLAGSVERKET_API_KEY`
- System works with mock data if not configured

## Features Overview

### Core Features ✅
- Company data integration (Bolagsverket API with mock data)
- AI-powered content generation for all PM sections
- Inline editing with version control
- Document export (Word/PDF)
- Complete audit logging system
- Financial analysis and forecasting
- Supabase authentication

### MVP Limitations
- Bolagsverket API uses mock data (easily configurable for real API)
- Basic financial forecasting (can be enhanced with more sophisticated models)
- Simple credit scoring model (configurable for bank-specific rules)

## Usage Guide

1. **Create New Credit PM**
   - Enter Swedish organization number (e.g., 556016-0680)
   - System fetches company data automatically
   - Optional: Set custom title

2. **Generate Content**
   - Click "Generate with AI" for each section
   - AI creates professional banking content
   - Edit content inline as needed

3. **Upload Financial Data**
   - Upload Excel/CSV files with financial history
   - System calculates ratios and forecasts
   - Financial analysis section updates automatically

4. **Export Documents**
   - Export to Word (.docx) or PDF formats
   - Includes metadata and audit trail
   - Professional banking format

## API Endpoints

### Cases
- `POST /api/v1/cases` - Create new case
- `GET /api/v1/cases` - List all cases
- `GET /api/v1/cases/{id}` - Get specific case

### Sections
- `POST /api/v1/sections/{case_id}/generate` - Generate AI content
- `PUT /api/v1/sections/{id}` - Update section content
- `GET /api/v1/sections/{case_id}` - Get all sections for case

### Export
- `POST /api/v1/export/{case_id}/word` - Export to Word
- `POST /api/v1/export/{case_id}/pdf` - Export to PDF

### Audit
- `GET /api/v1/audit/cases/{id}/trail` - Get case audit trail
- `GET /api/v1/audit/stats/ai-usage` - Get AI usage statistics

## Troubleshooting

### Common Issues

1. **Docker containers won't start**
   - Check Docker is running
   - Verify port availability (3000, 8000, 54322)
   - Check `.env` configuration

2. **Database connection errors**
   - Verify Supabase credentials
   - Check database initialization completed
   - Ensure RLS policies are configured

3. **AI generation not working**
   - Verify OpenAI API key is valid
   - Check API quota/billing
   - System falls back to placeholder text

4. **Authentication issues**
   - Check Supabase auth configuration
   - Verify JWT settings match
   - Clear browser cookies/localStorage

### Logs
- Frontend: `docker-compose logs frontend`
- Backend: `docker-compose logs backend`
- Database: `docker-compose logs db`

## Production Deployment

### Frontend (Netlify)
1. Connect GitHub repository
2. Set build command: `cd frontend && npm run build`
3. Set publish directory: `frontend/.next`
4. Configure environment variables

### Backend (Railway/Render)
1. Deploy from GitHub
2. Set startup command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Configure environment variables
4. Connect to Supabase database

### Database (Supabase)
- Already hosted and managed
- Configure production RLS policies
- Set up automated backups

## Next Steps

### Immediate Enhancements
1. Integrate real Bolagsverket API
2. Add UC/D&B risk data integration
3. Implement advanced financial models
4. Add policy engine for credit decisions

### Long-term Roadmap
1. RAG system for company website analysis
2. Automated market research
3. Advanced scenario modeling
4. Integration with core banking systems

## Support

For setup issues or questions:
1. Check this documentation
2. Review API documentation at `/docs`
3. Check the troubleshooting section
4. Review system logs