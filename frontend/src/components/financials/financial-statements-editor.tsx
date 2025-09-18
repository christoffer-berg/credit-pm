'use client'

import { useState, useEffect } from 'react'
import { useSupabaseClient } from '@supabase/auth-helpers-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save, Plus, Trash2, Calendar } from 'lucide-react'

interface FinancialStatement {
  id?: string
  year: number
  period_start: string
  period_end: string
  
  // Income statement
  revenue?: number
  cost_of_goods_sold?: number
  gross_profit?: number
  operating_expenses?: number
  ebitda?: number
  depreciation?: number
  ebit?: number
  financial_income?: number
  financial_expenses?: number
  profit_before_tax?: number
  tax_expense?: number
  net_profit?: number
  
  // Balance sheet
  current_assets?: number
  fixed_assets?: number
  total_assets?: number
  current_liabilities?: number
  long_term_liabilities?: number
  total_liabilities?: number
  equity?: number
  
  // Cash flow
  operating_cash_flow?: number
  investing_cash_flow?: number
  financing_cash_flow?: number
  net_cash_flow?: number
  cash_beginning?: number
  cash_ending?: number
  
  // Additional info
  employees?: number
  currency?: string
  is_consolidated?: boolean
  source?: string
}

interface FinancialStatementsEditorProps {
  companyId: string
  existingData?: FinancialStatement[]
  onSave?: () => void
}

const emptyStatement = (year: number): FinancialStatement => ({
  year,
  period_start: `${year}-01-01`,
  period_end: `${year}-12-31`,
  currency: 'SEK',
  is_consolidated: false,
  source: 'manual'
})

export function FinancialStatementsEditor({ companyId, existingData = [], onSave }: FinancialStatementsEditorProps) {
  const [statements, setStatements] = useState<FinancialStatement[]>([])
  const [activeYear, setActiveYear] = useState<number>(new Date().getFullYear() - 1)
  const [saving, setSaving] = useState(false)
  const supabase = useSupabaseClient()

  useEffect(() => {
    if (existingData.length > 0) {
      setStatements(existingData)
      setActiveYear(Math.max(...existingData.map(s => s.year)))
    } else {
      setStatements([emptyStatement(new Date().getFullYear() - 1)])
    }
  }, [existingData])

  const addYear = () => {
    const newYear = Math.max(...statements.map(s => s.year), new Date().getFullYear() - 1) + 1
    setStatements([...statements, emptyStatement(newYear)])
    setActiveYear(newYear)
  }

  const removeYear = (year: number) => {
    setStatements(statements.filter(s => s.year !== year))
    if (activeYear === year && statements.length > 1) {
      const remainingYears = statements.filter(s => s.year !== year).map(s => s.year)
      setActiveYear(Math.max(...remainingYears))
    }
  }

  const updateStatement = (year: number, field: keyof FinancialStatement, value: any) => {
    setStatements(statements.map(stmt => 
      stmt.year === year 
        ? { ...stmt, [field]: value === '' ? undefined : value }
        : stmt
    ))
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const session = await supabase.auth.getSession()
      
      for (const statement of statements) {
        const response = await fetch(`/api/v1/financials/companies/${companyId}/statements`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.data.session?.access_token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(statement)
        })
        
        if (!response.ok) {
          throw new Error(`Failed to save statement for ${statement.year}`)
        }
      }

      onSave?.()
    } catch (error) {
      console.error('Error saving statements:', error)
      alert('Failed to save financial statements')
    } finally {
      setSaving(false)
    }
  }

  const currentStatement = statements.find(s => s.year === activeYear) || emptyStatement(activeYear)
  const availableYears = statements.map(s => s.year).sort((a, b) => b - a)

  const formatNumber = (value: number | undefined): string => {
    return value ? (value / 1000000).toFixed(2) : ''
  }

  const parseNumber = (value: string): number | undefined => {
    const num = parseFloat(value)
    return isNaN(num) ? undefined : num * 1000000
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Financial Statements Editor</h3>
          <p className="text-sm text-muted-foreground">
            Enter financial data in millions SEK (e.g., 100.5 for 100.5M SEK)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={addYear} variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Year
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save All'}
          </Button>
        </div>
      </div>

      {/* Year Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Select Year</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {availableYears.map(year => (
              <div key={year} className="flex items-center gap-2">
                <Button
                  variant={year === activeYear ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveYear(year)}
                >
                  {year}
                </Button>
                {statements.length > 1 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeYear(year)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Statement Editor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Financial Statement - {activeYear}
          </CardTitle>
          <div className="flex gap-4">
            <div className="space-y-1">
              <Label htmlFor="period-start">Period Start</Label>
              <Input
                id="period-start"
                type="date"
                value={currentStatement.period_start}
                onChange={(e) => updateStatement(activeYear, 'period_start', e.target.value)}
                className="w-40"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="period-end">Period End</Label>
              <Input
                id="period-end"
                type="date"
                value={currentStatement.period_end}
                onChange={(e) => updateStatement(activeYear, 'period_end', e.target.value)}
                className="w-40"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="currency">Currency</Label>
              <Select value={currentStatement.currency} onValueChange={(value) => updateStatement(activeYear, 'currency', value)}>
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="SEK">SEK</SelectItem>
                  <SelectItem value="EUR">EUR</SelectItem>
                  <SelectItem value="USD">USD</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="income" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="income">Income Statement</TabsTrigger>
              <TabsTrigger value="balance">Balance Sheet</TabsTrigger>
              <TabsTrigger value="cashflow">Cash Flow</TabsTrigger>
            </TabsList>

            <TabsContent value="income" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="revenue">Revenue (MSEK)</Label>
                    <Input
                      id="revenue"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.revenue)}
                      onChange={(e) => updateStatement(activeYear, 'revenue', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="cogs">Cost of Goods Sold (MSEK)</Label>
                    <Input
                      id="cogs"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.cost_of_goods_sold)}
                      onChange={(e) => updateStatement(activeYear, 'cost_of_goods_sold', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="gross-profit">Gross Profit (MSEK)</Label>
                    <Input
                      id="gross-profit"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.gross_profit)}
                      onChange={(e) => updateStatement(activeYear, 'gross_profit', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="opex">Operating Expenses (MSEK)</Label>
                    <Input
                      id="opex"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.operating_expenses)}
                      onChange={(e) => updateStatement(activeYear, 'operating_expenses', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="ebitda">EBITDA (MSEK)</Label>
                    <Input
                      id="ebitda"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.ebitda)}
                      onChange={(e) => updateStatement(activeYear, 'ebitda', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="depreciation">Depreciation (MSEK)</Label>
                    <Input
                      id="depreciation"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.depreciation)}
                      onChange={(e) => updateStatement(activeYear, 'depreciation', parseNumber(e.target.value))}
                    />
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="ebit">EBIT (MSEK)</Label>
                    <Input
                      id="ebit"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.ebit)}
                      onChange={(e) => updateStatement(activeYear, 'ebit', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="financial-income">Financial Income (MSEK)</Label>
                    <Input
                      id="financial-income"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.financial_income)}
                      onChange={(e) => updateStatement(activeYear, 'financial_income', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="financial-expenses">Financial Expenses (MSEK)</Label>
                    <Input
                      id="financial-expenses"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.financial_expenses)}
                      onChange={(e) => updateStatement(activeYear, 'financial_expenses', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="profit-before-tax">Profit Before Tax (MSEK)</Label>
                    <Input
                      id="profit-before-tax"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.profit_before_tax)}
                      onChange={(e) => updateStatement(activeYear, 'profit_before_tax', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="tax-expense">Tax Expense (MSEK)</Label>
                    <Input
                      id="tax-expense"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.tax_expense)}
                      onChange={(e) => updateStatement(activeYear, 'tax_expense', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="net-profit">Net Profit (MSEK)</Label>
                    <Input
                      id="net-profit"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.net_profit)}
                      onChange={(e) => updateStatement(activeYear, 'net_profit', parseNumber(e.target.value))}
                    />
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="balance" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h4 className="font-semibold">Assets</h4>
                  <div>
                    <Label htmlFor="current-assets">Current Assets (MSEK)</Label>
                    <Input
                      id="current-assets"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.current_assets)}
                      onChange={(e) => updateStatement(activeYear, 'current_assets', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="fixed-assets">Fixed Assets (MSEK)</Label>
                    <Input
                      id="fixed-assets"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.fixed_assets)}
                      onChange={(e) => updateStatement(activeYear, 'fixed_assets', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="total-assets">Total Assets (MSEK)</Label>
                    <Input
                      id="total-assets"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.total_assets)}
                      onChange={(e) => updateStatement(activeYear, 'total_assets', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="employees">Employees</Label>
                    <Input
                      id="employees"
                      type="number"
                      placeholder="0"
                      value={currentStatement.employees || ''}
                      onChange={(e) => updateStatement(activeYear, 'employees', e.target.value ? parseInt(e.target.value) : undefined)}
                    />
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-semibold">Liabilities & Equity</h4>
                  <div>
                    <Label htmlFor="current-liabilities">Current Liabilities (MSEK)</Label>
                    <Input
                      id="current-liabilities"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.current_liabilities)}
                      onChange={(e) => updateStatement(activeYear, 'current_liabilities', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="long-term-liabilities">Long-term Liabilities (MSEK)</Label>
                    <Input
                      id="long-term-liabilities"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.long_term_liabilities)}
                      onChange={(e) => updateStatement(activeYear, 'long_term_liabilities', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="total-liabilities">Total Liabilities (MSEK)</Label>
                    <Input
                      id="total-liabilities"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.total_liabilities)}
                      onChange={(e) => updateStatement(activeYear, 'total_liabilities', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="equity">Equity (MSEK)</Label>
                    <Input
                      id="equity"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.equity)}
                      onChange={(e) => updateStatement(activeYear, 'equity', parseNumber(e.target.value))}
                    />
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="cashflow" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="operating-cash-flow">Operating Cash Flow (MSEK)</Label>
                    <Input
                      id="operating-cash-flow"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.operating_cash_flow)}
                      onChange={(e) => updateStatement(activeYear, 'operating_cash_flow', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="investing-cash-flow">Investing Cash Flow (MSEK)</Label>
                    <Input
                      id="investing-cash-flow"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.investing_cash_flow)}
                      onChange={(e) => updateStatement(activeYear, 'investing_cash_flow', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="financing-cash-flow">Financing Cash Flow (MSEK)</Label>
                    <Input
                      id="financing-cash-flow"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.financing_cash_flow)}
                      onChange={(e) => updateStatement(activeYear, 'financing_cash_flow', parseNumber(e.target.value))}
                    />
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="net-cash-flow">Net Cash Flow (MSEK)</Label>
                    <Input
                      id="net-cash-flow"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.net_cash_flow)}
                      onChange={(e) => updateStatement(activeYear, 'net_cash_flow', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="cash-beginning">Cash Beginning (MSEK)</Label>
                    <Input
                      id="cash-beginning"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.cash_beginning)}
                      onChange={(e) => updateStatement(activeYear, 'cash_beginning', parseNumber(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="cash-ending">Cash Ending (MSEK)</Label>
                    <Input
                      id="cash-ending"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formatNumber(currentStatement.cash_ending)}
                      onChange={(e) => updateStatement(activeYear, 'cash_ending', parseNumber(e.target.value))}
                    />
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}