# Edit Page 404 Fix

## Problem
When clicking "Edit" on a case from the dashboard, users were getting a 404 page because the case detail page didn't exist for the Pages Router architecture.

## Root Cause
The frontend uses Next.js Pages Router, but the case detail page only existed in the `src/app.backup` directory (App Router). The `CaseList` component was linking to `/cases/${pmCase.id}`, but there was no corresponding page at `/pages/cases/[id].tsx`.

## Solution Implemented

### 1. Created Missing Page
- **File**: `/pages/cases/[id].tsx`
- **Purpose**: Case detail page for editing PM sections
- **Features**:
  - Dynamic routing with case ID
  - Complete PM generation with "Generate Complete PM" button
  - Individual section generation
  - Section editing with save functionality
  - Error handling and loading states

### 2. Created Simplified Section Editor
- **File**: `/src/components/cases/simple-section-editor.tsx`
- **Purpose**: Section editor without Supabase/TanStack dependencies
- **Features**:
  - Inline text editing with textarea
  - Save changes functionality
  - AI content vs user content comparison
  - Regeneration capability
  - Status indicators (Modified, AI Generated)

### 3. Page Features
- **Navigation**: Back button to dashboard
- **Case Info**: Title, status badge, version
- **Complete Generation**: Single button to generate all 6 sections
- **Individual Sections**: Generate/edit each section independently
- **Section Types**:
  - Purpose
  - Business Description  
  - Market Analysis
  - Financial Analysis
  - Credit Analysis
  - Credit Proposal

### 4. API Integration
The page integrates with the backend APIs:
- `GET /api/v1/cases/{id}` - Fetch case details
- `GET /api/v1/sections/{id}` - Fetch case sections
- `POST /api/v1/cases/{id}/generate` - Generate complete PM
- `POST /api/v1/sections/{id}/generate` - Generate individual section
- `PUT /api/v1/sections/{section_id}` - Update section content

## File Structure
```
frontend/
├── pages/
│   └── cases/
│       └── [id].tsx          # ✅ NEW - Case detail page
└── src/
    └── components/
        └── cases/
            └── simple-section-editor.tsx  # ✅ NEW - Simplified editor
```

## Result
✅ Edit buttons now navigate to functional case detail pages
✅ Users can generate complete PMs with one click  
✅ Individual sections can be generated and edited
✅ Changes are saved automatically with visual feedback
✅ AI content can be compared with user modifications