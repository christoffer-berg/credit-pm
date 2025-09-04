# Credit PM Generation API

## Complete PM Generation

### Endpoint: `POST /cases/{case_id}/generate`

Generates a complete Credit PM with all six standard sections for a given case.

#### Authentication
Requires valid JWT token in Authorization header.

#### Request
- **Method**: POST
- **URL**: `/cases/{case_id}/generate`
- **Headers**: 
  - `Authorization: Bearer <jwt_token>`
  - `Content-Type: application/json`

#### Response
Returns a JSON object with the generation result:

```json
{
  "case_id": "uuid",
  "status": "success",
  "sections": {
    "purpose": {
      "id": "uuid",
      "section_type": "purpose",
      "title": "Purpose",
      "ai_content": "Generated purpose content...",
      "version": 1
    },
    "business_description": {
      "id": "uuid", 
      "section_type": "business_description",
      "title": "Business Description",
      "ai_content": "Generated business description...",
      "version": 1
    },
    "market_analysis": {
      "id": "uuid",
      "section_type": "market_analysis", 
      "title": "Market Analysis",
      "ai_content": "Generated market analysis...",
      "version": 1
    },
    "financial_analysis": {
      "id": "uuid",
      "section_type": "financial_analysis",
      "title": "Financial Analysis", 
      "ai_content": "Generated financial analysis with ratios and forecasts...",
      "version": 1
    },
    "credit_analysis": {
      "id": "uuid",
      "section_type": "credit_analysis",
      "title": "Credit Analysis",
      "ai_content": "Generated credit risk analysis with score...",
      "version": 1
    },
    "credit_proposal": {
      "id": "uuid",
      "section_type": "credit_proposal", 
      "title": "Credit Proposal",
      "ai_content": "Generated credit proposal with recommendation...",
      "version": 1
    }
  },
  "message": "Generated 6 sections successfully"
}
```

#### Features

1. **Financial Integration**: Automatically calculates financial ratios, credit scores, and forecasts from uploaded financial data
2. **Contextual AI Generation**: Each section uses comprehensive context including:
   - Company information from Bolagsverket API
   - Historical financial data and calculated ratios
   - Credit scoring based on financial metrics
   - Financial forecasts using Prophet/LightGBM models
3. **Version Management**: Tracks versions of AI-generated content
4. **Error Handling**: Continues generating other sections even if one fails
5. **Audit Trail**: Logs all AI generation activities with prompts and responses

#### Prerequisites

Before generating a PM:
1. Create a case with `POST /cases/` using an organization number
2. Optionally upload financial data with `POST /financials/{company_id}/upload`

#### Error Responses

- `404 Not Found`: Case not found
- `400 Bad Request`: Generation error with details
- `401 Unauthorized`: Invalid or missing authentication token

## Usage Example

```bash
# 1. Create a case
curl -X POST "http://localhost:8000/cases/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"organization_number": "5566778899", "title": "Credit PM for Test Company"}'

# Response: {"id": "case-uuid", ...}

# 2. Generate complete PM
curl -X POST "http://localhost:8000/cases/case-uuid/generate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"

# Response: Complete PM sections as JSON
```

## Section Types Generated

1. **Purpose**: Brief statement explaining why the credit analysis is conducted
2. **Business Description**: Comprehensive overview of company operations, market position, and business model  
3. **Market Analysis**: Industry outlook, competitive landscape, and market risks/opportunities
4. **Financial Analysis**: Detailed analysis with historical data, ratios, forecasts, and trends
5. **Credit Analysis**: Risk assessment with credit scoring, risk factors, and rating recommendation
6. **Credit Proposal**: Final recommendation with facility details, terms, and approval decision

Each section is generated with professional banking language and specific quantitative insights where financial data is available.