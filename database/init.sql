-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    business_description TEXT,
    industry_code VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- PM Cases table
CREATE TABLE IF NOT EXISTS pm_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed', 'exported')),
    version INTEGER DEFAULT 1,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- PM Sections table
CREATE TABLE IF NOT EXISTS pm_sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES pm_cases(id) ON DELETE CASCADE,
    section_type VARCHAR(50) NOT NULL CHECK (section_type IN ('purpose', 'business_description', 'market_analysis', 'financial_analysis', 'credit_analysis', 'credit_proposal')),
    title VARCHAR(255) NOT NULL,
    ai_content TEXT,
    user_content TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(case_id, section_type)
);

-- Financial data table
CREATE TABLE IF NOT EXISTS financials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    revenue DECIMAL(15,2),
    profit DECIMAL(15,2),
    assets DECIMAL(15,2),
    liabilities DECIMAL(15,2),
    equity DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, year)
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES pm_cases(id),
    section_id UUID REFERENCES pm_sections(id),
    action VARCHAR(100) NOT NULL,
    prompt TEXT,
    ai_response TEXT,
    model_version VARCHAR(50),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document embeddings for RAG
CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    content TEXT NOT NULL,
    embedding vector(1536),
    source VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_companies_org_number ON companies(organization_number);
CREATE INDEX IF NOT EXISTS idx_pm_cases_company_id ON pm_cases(company_id);
CREATE INDEX IF NOT EXISTS idx_pm_cases_status ON pm_cases(status);
CREATE INDEX IF NOT EXISTS idx_pm_sections_case_id ON pm_sections(case_id);
CREATE INDEX IF NOT EXISTS idx_financials_company_year ON financials(company_id, year);
CREATE INDEX IF NOT EXISTS idx_audit_log_case_id ON audit_log(case_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_company_id ON document_embeddings(company_id);

-- Row Level Security (RLS) policies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE pm_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE pm_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE financials ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Policies for authenticated users
CREATE POLICY "Users can view all companies" ON companies FOR SELECT TO authenticated USING (true);
CREATE POLICY "Users can create companies" ON companies FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Users can update companies" ON companies FOR UPDATE TO authenticated USING (true);

CREATE POLICY "Users can view all PM cases" ON pm_cases FOR SELECT TO authenticated USING (true);
CREATE POLICY "Users can create PM cases" ON pm_cases FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Users can update PM cases" ON pm_cases FOR UPDATE TO authenticated USING (true);

CREATE POLICY "Users can view PM sections" ON pm_sections FOR SELECT TO authenticated USING (true);
CREATE POLICY "Users can create PM sections" ON pm_sections FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Users can update PM sections" ON pm_sections FOR UPDATE TO authenticated USING (true);

CREATE POLICY "Users can view financials" ON financials FOR SELECT TO authenticated USING (true);
CREATE POLICY "Users can create financials" ON financials FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Users can update financials" ON financials FOR UPDATE TO authenticated USING (true);

CREATE POLICY "Users can view audit logs" ON audit_log FOR SELECT TO authenticated USING (true);
CREATE POLICY "Users can create audit logs" ON audit_log FOR INSERT TO authenticated WITH CHECK (true);

-- Functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating timestamps
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pm_cases_updated_at BEFORE UPDATE ON pm_cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pm_sections_updated_at BEFORE UPDATE ON pm_sections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_financials_updated_at BEFORE UPDATE ON financials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();