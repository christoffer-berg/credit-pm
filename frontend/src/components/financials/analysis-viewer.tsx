'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { FileText, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Wand2, BarChart3 } from 'lucide-react'

interface AnalysisViewerProps {
  companyId: string
  analysis: any
  onGenerate: () => void
  isGenerating: boolean
}

interface FinancialAnalysis {
  id: string
  company_id: string
  analysis_type: string
  summary: string
  key_metrics: Record<string, any>
  risk_assessment: {
    overall_risk: string
    risk_factors: string[]
    risk_score: number
  }
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  created_at: string
  updated_at: string
}

export function AnalysisViewer({ companyId, analysis, onGenerate, isGenerating }: AnalysisViewerProps) {
  if (!analysis) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            AI Financial Analysis
          </CardTitle>
          <CardDescription>
            Generate comprehensive AI-powered financial analysis with risk assessment and recommendations
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center py-8">
          <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Generated</h3>
          <p className="text-gray-500 mb-6 max-w-md mx-auto">
            Generate a comprehensive financial analysis that includes risk assessment, 
            key performance indicators, market position analysis, and strategic recommendations.
          </p>
          <Button onClick={onGenerate} disabled={isGenerating} size="lg">
            <Wand2 className="h-4 w-4 mr-2" />
            {isGenerating ? 'Generating Analysis...' : 'Generate AI Analysis'}
          </Button>
        </CardContent>
      </Card>
    )
  }

  const getRiskColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'high':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getRiskIcon = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'low':
        return <CheckCircle className="h-4 w-4" />
      case 'medium':
        return <AlertTriangle className="h-4 w-4" />
      case 'high':
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  const formatMetricValue = (key: string, value: any) => {
    if (typeof value === 'number') {
      if (key.includes('ratio') || key.includes('margin') || key.includes('percent')) {
        return `${(value * 100).toFixed(1)}%`
      }
      if (key.includes('amount') || key.includes('value')) {
        return new Intl.NumberFormat('sv-SE', {
          style: 'currency',
          currency: 'SEK',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(value)
      }
      return value.toFixed(2)
    }
    return String(value)
  }

  return (
    <div className="space-y-6">
      {/* Header with Summary */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                AI Financial Analysis
              </CardTitle>
              <CardDescription>
                Generated on {new Date(analysis.created_at).toLocaleDateString('sv-SE')}
              </CardDescription>
            </div>
            <div className="text-right space-y-1">
              <Badge className={getRiskColor(analysis.risk_assessment?.overall_risk)}>
                <div className="flex items-center gap-1">
                  {getRiskIcon(analysis.risk_assessment?.overall_risk)}
                  {analysis.risk_assessment?.overall_risk} Risk
                </div>
              </Badge>
              <div className="block">
                <Button onClick={onGenerate} disabled={isGenerating} size="sm" variant="outline">
                  <Wand2 className="h-4 w-4 mr-2" />
                  Regenerate
                </Button>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="prose max-w-none">
            <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      {analysis.key_metrics && Object.keys(analysis.key_metrics).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Key Financial Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(analysis.key_metrics).map(([key, value]) => (
                <div key={key} className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm font-medium text-gray-600 mb-1">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </div>
                  <div className="text-lg font-bold text-gray-900">
                    {formatMetricValue(key, value)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Risk Assessment */}
      {analysis.risk_assessment && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Risk Assessment</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                  {getRiskIcon(analysis.risk_assessment.overall_risk)}
                  <span className="font-medium">Overall Risk Level</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={getRiskColor(analysis.risk_assessment.overall_risk)}>
                    {analysis.risk_assessment.overall_risk}
                  </Badge>
                  {analysis.risk_assessment.risk_score && (
                    <span className="text-sm text-gray-600">
                      Score: {analysis.risk_assessment.risk_score}/10
                    </span>
                  )}
                </div>
              </div>

              {analysis.risk_assessment.risk_factors && analysis.risk_assessment.risk_factors.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Key Risk Factors</h4>
                  <ul className="space-y-2">
                    {analysis.risk_assessment.risk_factors.map((factor: string, index: number) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <AlertTriangle className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Strengths and Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths */}
        {analysis.strengths && analysis.strengths.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                Strengths
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {analysis.strengths.map((strength: string, index: number) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Weaknesses */}
        {analysis.weaknesses && analysis.weaknesses.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-red-500" />
                Areas for Improvement
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {analysis.weaknesses.map((weakness: string, index: number) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <span>{weakness}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recommendations */}
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Strategic Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analysis.recommendations.map((recommendation: string, index: number) => (
                <div key={index} className="p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-start gap-2">
                    <div className="h-6 w-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
                      {index + 1}
                    </div>
                    <p className="text-sm text-blue-800">{recommendation}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Metadata */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div>Analysis Type: {analysis.analysis_type}</div>
            <div>Last Updated: {new Date(analysis.updated_at).toLocaleDateString('sv-SE')}</div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}