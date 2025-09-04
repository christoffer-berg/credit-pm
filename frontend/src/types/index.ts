export interface Company {
  id: string
  organization_number: string
  name: string
  business_description?: string
  industry_code?: string
  created_at: string
  updated_at: string
}

export interface PMCase {
  id: string
  company_id: string
  title: string
  status: 'draft' | 'in_progress' | 'completed' | 'exported'
  version: number
  created_by: string
  created_at: string
  updated_at: string
  company?: Company
}

export interface PMSection {
  id: string
  case_id: string
  section_type: 'purpose' | 'business_description' | 'market_analysis' | 'financial_analysis' | 'credit_analysis' | 'credit_proposal'
  title: string
  ai_content?: string
  user_content?: string
  version: number
  created_at: string
  updated_at: string
}

export interface Financial {
  id: string
  company_id: string
  year: number
  revenue?: number
  profit?: number
  assets?: number
  liabilities?: number
  equity?: number
  created_at: string
  updated_at: string
}

export interface AuditLog {
  id: string
  case_id: string
  section_id?: string
  action: string
  prompt?: string
  ai_response?: string
  model_version?: string
  user_id: string
  created_at: string
}

export interface CreatePMCaseRequest {
  organization_number: string
  title?: string
}

export interface UpdateSectionRequest {
  user_content: string
}