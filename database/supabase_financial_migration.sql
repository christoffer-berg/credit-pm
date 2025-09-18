-- Financial tables migration for Supabase
-- Run this in your Supabase SQL editor

-- Enhanced financial statements table
CREATE TABLE IF NOT EXISTS financial_statements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Income statement
    revenue DECIMAL(18,2),
    cost_of_goods_sold DECIMAL(18,2),
    gross_profit DECIMAL(18,2),
    operating_expenses DECIMAL(18,2),
    ebitda DECIMAL(18,2),
    depreciation DECIMAL(18,2),
    ebit DECIMAL(18,2),
    financial_income DECIMAL(18,2),
    financial_expenses DECIMAL(18,2),
    profit_before_tax DECIMAL(18,2),
    tax_expense DECIMAL(18,2),
    net_profit DECIMAL(18,2),
    
    -- Balance sheet
    current_assets DECIMAL(18,2),
    fixed_assets DECIMAL(18,2),
    total_assets DECIMAL(18,2),
    current_liabilities DECIMAL(18,2),
    long_term_liabilities DECIMAL(18,2),
    total_liabilities DECIMAL(18,2),
    equity DECIMAL(18,2),
    
    -- Cash flow
    operating_cash_flow DECIMAL(18,2),
    investing_cash_flow DECIMAL(18,2),
    financing_cash_flow DECIMAL(18,2),
    net_cash_flow DECIMAL(18,2),
    cash_beginning DECIMAL(18,2),
    cash_ending DECIMAL(18,2),
    
    -- Additional info
    employees INTEGER,
    currency VARCHAR(3) DEFAULT 'SEK',
    is_consolidated BOOLEAN DEFAULT false,
    source VARCHAR(50) DEFAULT 'manual' CHECK (source IN ('manual', 'allabolag', 'pdf_upload')),
    source_document VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, year)
);

-- Financial projections table
CREATE TABLE IF NOT EXISTS financial_projections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    
    -- Growth assumptions
    revenue_growth DECIMAL(5,4),  -- e.g., 0.0500 for 5%
    margin_assumptions JSONB DEFAULT '{}',
    
    -- Projected values
    projected_revenue DECIMAL(18,2),
    projected_ebitda DECIMAL(18,2),
    projected_net_profit DECIMAL(18,2),
    projected_assets DECIMAL(18,2),
    projected_equity DECIMAL(18,2),
    
    -- Metadata
    assumptions TEXT[],
    confidence_level VARCHAR(10) DEFAULT 'medium' CHECK (confidence_level IN ('low', 'medium', 'high')),
    methodology VARCHAR(50) DEFAULT 'trend_analysis',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, year)
);

-- PDF documents table for file uploads
CREATE TABLE IF NOT EXISTS financial_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    
    -- Processing status
    parsing_status VARCHAR(20) DEFAULT 'pending' CHECK (parsing_status IN ('pending', 'processing', 'completed', 'failed')),
    extracted_data JSONB,
    error_message TEXT,
    
    -- Metadata
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_date TIMESTAMP WITH TIME ZONE,
    uploaded_by UUID REFERENCES auth.users(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial analysis results table
CREATE TABLE IF NOT EXISTS financial_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    case_id UUID REFERENCES pm_cases(id),
    
    -- Analysis content
    analysis_text TEXT,
    key_metrics JSONB DEFAULT '{}',
    
    -- Historical data reference
    years_analyzed INTEGER[],
    projection_years INTEGER[],
    
    -- AI generation info
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_used VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_financial_statements_company_year ON financial_statements(company_id, year);
CREATE INDEX IF NOT EXISTS idx_financial_statements_source ON financial_statements(source);
CREATE INDEX IF NOT EXISTS idx_financial_projections_company_year ON financial_projections(company_id, year);
CREATE INDEX IF NOT EXISTS idx_financial_documents_company ON financial_documents(company_id);
CREATE INDEX IF NOT EXISTS idx_financial_documents_status ON financial_documents(parsing_status);
CREATE INDEX IF NOT EXISTS idx_financial_analyses_company ON financial_analyses(company_id);
CREATE INDEX IF NOT EXISTS idx_financial_analyses_case ON financial_analyses(case_id);

-- Enable Row Level Security (RLS)
ALTER TABLE financial_statements ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_projections ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_analyses ENABLE ROW LEVEL SECURITY;

-- RLS Policies for authenticated users
CREATE POLICY "Users can view financial statements" ON financial_statements FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can create financial statements" ON financial_statements FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update financial statements" ON financial_statements FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Users can delete financial statements" ON financial_statements FOR DELETE USING (auth.role() = 'authenticated');

CREATE POLICY "Users can view financial projections" ON financial_projections FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can create financial projections" ON financial_projections FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update financial projections" ON financial_projections FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Users can delete financial projections" ON financial_projections FOR DELETE USING (auth.role() = 'authenticated');

CREATE POLICY "Users can view financial documents" ON financial_documents FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can create financial documents" ON financial_documents FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update financial documents" ON financial_documents FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Users can delete financial documents" ON financial_documents FOR DELETE USING (auth.role() = 'authenticated');

CREATE POLICY "Users can view financial analyses" ON financial_analyses FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can create financial analyses" ON financial_analyses FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update financial analyses" ON financial_analyses FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Users can delete financial analyses" ON financial_analyses FOR DELETE USING (auth.role() = 'authenticated');