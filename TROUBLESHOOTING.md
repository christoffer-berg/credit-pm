# Troubleshooting Issues

## Problem 1: 404 when editing cases
**Status**: ✅ FIXED
- **Issue**: Missing case detail page at `/pages/cases/[id].tsx` 
- **Solution**: Created the missing page with full PM editing functionality

## Problem 2: Case creation not generating content
**Status**: 🔍 INVESTIGATING

### Root Causes Identified:
1. **Authentication**: All endpoints required auth tokens, but frontend wasn't sending them
2. **API Routing**: Frontend API calls need to be proxied to backend
3. **Backend not running**: Need to ensure FastAPI backend is running

### Fixes Applied:
1. **✅ Added API proxy** in `next.config.js`:
   ```javascript
   async rewrites() {
     return [
       {
         source: '/api/v1/:path*',
         destination: 'http://localhost:8000/api/v1/:path*',
       },
     ]
   }
   ```

2. **✅ Disabled auth for development** in backend:
   - Set `REQUIRE_AUTH=false` environment variable
   - Updated all route handlers to use optional authentication
   - Mock user ID: "dev-user" for development

3. **✅ Fixed dependency injection** in backend routes:
   - Created `optional_auth()` function
   - Updated all endpoints to use optional auth

### Next Steps to Test:
1. Start the FastAPI backend: `cd backend && uvicorn main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Test case creation with org number: `556016-0680` (ICA Gruppen)
4. Test PM generation using the "Generate Complete PM" button

### Expected Flow:
1. **Create Case**: POST `/api/v1/cases` → Creates company + case records
2. **Generate PM**: POST `/api/v1/cases/{id}/generate` → Creates all 6 sections with AI content
3. **Edit Sections**: Individual section editing with save functionality

### Debugging Commands:
```bash
# Check if backend is running
curl http://localhost:8000/health

# Test case creation
curl -X POST http://localhost:8000/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{"organization_number": "5560160680", "title": "Test PM"}'

# Test case retrieval
curl http://localhost:8000/api/v1/cases

# Test PM generation
curl -X POST http://localhost:8000/api/v1/cases/{case-id}/generate
```

### Environment Variables Needed:
```
REQUIRE_AUTH=false
OPENAI_API_KEY=your_key_here  # Optional, will show placeholders if missing
```