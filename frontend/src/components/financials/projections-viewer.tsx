'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Minus, AlertCircle, Wand2 } from 'lucide-react'

interface ProjectionsViewerProps {
  companyId: string
  projections: any[]
  onGenerate: () => void
  isGenerating: boolean
}

interface ProjectionData {
  id: string
  company_id: string
  projection_year: number
  revenue: number
  gross_profit: number
  operating_profit: number
  net_profit: number
  total_assets: number
  total_equity: number
  total_liabilities: number
  cash_flow_operating: number
  confidence_level: string
  methodology: string
  assumptions: Record<string, any>
  created_at: string
}

export function ProjectionsViewer({ companyId, projections, onGenerate, isGenerating }: ProjectionsViewerProps) {
  if (!projections || projections.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            5-Year Financial Projections
          </CardTitle>
          <CardDescription>
            Generate AI-powered financial forecasts based on historical data and market trends
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center py-8">
          <TrendingUp className="h-16 w-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Projections Generated</h3>
          <p className="text-gray-500 mb-6 max-w-md mx-auto">
            Generate 5-year financial projections using advanced forecasting algorithms that consider 
            historical trends, industry benchmarks, and economic indicators.
          </p>
          <Button onClick={onGenerate} disabled={isGenerating} size="lg">
            <Wand2 className="h-4 w-4 mr-2" />
            {isGenerating ? 'Generating Projections...' : 'Generate 5-Year Projections'}
          </Button>
        </CardContent>
      </Card>
    )
  }

  // Sort projections by year
  const sortedProjections = [...projections].sort((a, b) => a.projection_year - b.projection_year)
  const latestProjection = sortedProjections[sortedProjections.length - 1]

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('sv-SE', {
      style: 'currency',
      currency: 'SEK',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatMillions = (amount: number) => {
    return `${(amount / 1000000).toFixed(1)}M SEK`
  }

  const getTrendIcon = (current: number, previous: number) => {
    if (current > previous) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (current < previous) return <TrendingDown className="h-4 w-4 text-red-500" />
    return <Minus className="h-4 w-4 text-gray-500" />
  }

  const getConfidenceColor = (confidence: string) => {
    switch (confidence?.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header with Summary */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                5-Year Financial Projections
              </CardTitle>
              <CardDescription>
                Generated on {new Date(latestProjection.created_at).toLocaleDateString('sv-SE')}
              </CardDescription>
            </div>
            <div className="text-right space-y-1">
              <Badge className={getConfidenceColor(latestProjection.confidence_level)}>
                {latestProjection.confidence_level} Confidence
              </Badge>
              <Button onClick={onGenerate} disabled={isGenerating} size="sm" variant="outline">
                <Wand2 className="h-4 w-4 mr-2" />
                Regenerate
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {formatMillions(latestProjection.revenue)}
              </div>
              <div className="text-sm text-gray-500">Projected Revenue ({latestProjection.projection_year})</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {formatMillions(latestProjection.operating_profit)}
              </div>
              <div className="text-sm text-gray-500">Operating Profit ({latestProjection.projection_year})</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {formatMillions(latestProjection.total_assets)}
              </div>
              <div className="text-sm text-gray-500">Total Assets ({latestProjection.projection_year})</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {latestProjection.methodology}
              </div>
              <div className="text-sm text-gray-500">Forecasting Method</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Projections Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Year-by-Year Projections</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Year</th>
                  <th className="text-right py-2">Revenue</th>
                  <th className="text-right py-2">Operating Profit</th>
                  <th className="text-right py-2">Net Profit</th>
                  <th className="text-right py-2">Total Assets</th>
                  <th className="text-right py-2">Cash Flow</th>
                </tr>
              </thead>
              <tbody>
                {sortedProjections.map((projection, index) => {
                  const previousProjection = index > 0 ? sortedProjections[index - 1] : null
                  
                  return (
                    <tr key={projection.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 font-medium">{projection.projection_year}</td>
                      <td className="text-right py-3">
                        <div className="flex items-center justify-end gap-2">
                          {formatMillions(projection.revenue)}
                          {previousProjection && getTrendIcon(projection.revenue, previousProjection.revenue)}
                        </div>
                      </td>
                      <td className="text-right py-3">
                        <div className="flex items-center justify-end gap-2">
                          {formatMillions(projection.operating_profit)}
                          {previousProjection && getTrendIcon(projection.operating_profit, previousProjection.operating_profit)}
                        </div>
                      </td>
                      <td className="text-right py-3">
                        <div className="flex items-center justify-end gap-2">
                          {formatMillions(projection.net_profit)}
                          {previousProjection && getTrendIcon(projection.net_profit, previousProjection.net_profit)}
                        </div>
                      </td>
                      <td className="text-right py-3">
                        <div className="flex items-center justify-end gap-2">
                          {formatMillions(projection.total_assets)}
                          {previousProjection && getTrendIcon(projection.total_assets, previousProjection.total_assets)}
                        </div>
                      </td>
                      <td className="text-right py-3">
                        <div className="flex items-center justify-end gap-2">
                          {formatMillions(projection.cash_flow_operating)}
                          {previousProjection && getTrendIcon(projection.cash_flow_operating, previousProjection.cash_flow_operating)}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Methodology and Assumptions */}
      {latestProjection.assumptions && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Methodology & Assumptions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Forecasting Method</h4>
                <Badge variant="outline">{latestProjection.methodology}</Badge>
              </div>

              {Object.keys(latestProjection.assumptions).length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Key Assumptions</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    {Object.entries(latestProjection.assumptions).map(([key, value]) => (
                      <div key={key} className="flex justify-between p-2 bg-gray-50 rounded">
                        <span className="font-medium">{key.replace(/_/g, ' ')}:</span>
                        <span>{typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-1">Important Note</p>
                  <p>
                    These projections are estimates based on historical data and market trends. 
                    Actual results may vary due to economic conditions, market changes, and company-specific factors.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}