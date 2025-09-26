'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
// Supabase client no longer needed here; apiClient handles auth
// import { useSupabaseClient } from '@supabase/auth-helpers-react'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Upload, Download, TrendingUp, BarChart3, FileText, Globe, Plus, Edit } from 'lucide-react'
import { FinancialStatementsEditor } from './financial-statements-editor'
import { PDFUploader } from './pdf-uploader'
import { AllabolagFetcher } from './allabolag-fetcher'
import { ProjectionsViewer } from './projections-viewer'
import { AnalysisViewer } from './analysis-viewer'

interface FinancialDataManagerProps {
  companyId: string
  companyName: string
  orgNumber?: string
}

interface FinancialOverview {
  company_id: string
  historical_statements: any[]
  projections: any[]
  latest_analysis: any
  uploaded_documents: any[]
  overview: {
    years_available: number
    has_projections: boolean
    has_analysis: boolean
    latest_year: number | null
  }
}

export function FinancialDataManager({ companyId, companyName, orgNumber }: FinancialDataManagerProps) {
  const [activeTab, setActiveTab] = useState('overview')
  const [showStatementsEditor, setShowStatementsEditor] = useState(false)
  const [prefillStatements, setPrefillStatements] = useState<any[] | undefined>(undefined)
  const [reviewDoc, setReviewDoc] = useState<any | null>(null)
  // const supabase = useSupabaseClient()
  const queryClient = useQueryClient()

  // Fetch financial overview
  const { data: overview, isLoading, error } = useQuery<FinancialOverview>({
    queryKey: ['financial-overview', companyId],
    queryFn: async () => apiClient.getFinancialOverview(companyId),
  })

  // Fetch uploaded documents (full data including extracted_data)
  const { data: documents } = useQuery<any[]>({
    queryKey: ['financial-documents', companyId],
    queryFn: async () => apiClient.getFinancialDocuments(companyId),
  })

  // Generate projections
  const generateProjections = useMutation({
    mutationFn: async () => apiClient.generateFinancialProjections(companyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['financial-overview', companyId] })
    },
  })

  // Generate AI analysis
  const generateAnalysis = useMutation({
    mutationFn: async () => apiClient.generateFinancialAnalysis(companyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['financial-overview', companyId] })
    },
  })

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">Loading financial data...</div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center text-red-600">
            Error loading financial data: {error.message}
          </div>
        </CardContent>
      </Card>
    )
  }

  const hasData = overview && overview.overview.years_available > 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Financial Data - {companyName}
          </CardTitle>
          <CardDescription>
            Manage financial statements, generate projections, and create AI-powered analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{overview?.overview.years_available || 0}</div>
              <div className="text-sm text-muted-foreground">Years Available</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{overview?.overview.latest_year || 'N/A'}</div>
              <div className="text-sm text-muted-foreground">Latest Year</div>
            </div>
            <div className="text-center">
              <Badge variant={overview?.overview.has_projections ? 'default' : 'secondary'}>
                {overview?.overview.has_projections ? 'Generated' : 'Not Generated'}
              </Badge>
              <div className="text-sm text-muted-foreground">Projections</div>
            </div>
            <div className="text-center">
              <Badge variant={overview?.overview.has_analysis ? 'default' : 'secondary'}>
                {overview?.overview.has_analysis ? 'Generated' : 'Not Generated'}
              </Badge>
              <div className="text-sm text-muted-foreground">AI Analysis</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Collection Section */}
      {!hasData && (
        <Card>
          <CardHeader>
            <CardTitle>Get Financial Data</CardTitle>
            <CardDescription>
              Start by collecting financial data using one of these methods:
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="p-4">
                <div className="text-center space-y-2">
                  <Globe className="h-8 w-8 mx-auto text-blue-500" />
                  <h3 className="font-semibold">Fetch from Allabolag</h3>
                  <p className="text-sm text-muted-foreground">
                    Automatically fetch financial data from allabolag.se
                  </p>
                  <AllabolagFetcher 
                    companyId={companyId} 
                    companyName={companyName}
                    orgNumber={orgNumber}
                    onSuccess={() => queryClient.invalidateQueries({ queryKey: ['financial-overview', companyId] })}
                  />
                </div>
              </Card>

              <Card className="p-4">
                <div className="text-center space-y-2">
                  <Upload className="h-8 w-8 mx-auto text-green-500" />
                  <h3 className="font-semibold">Upload PDF</h3>
                  <p className="text-sm text-muted-foreground">
                    Upload annual report PDFs for automatic parsing
                  </p>
                  <PDFUploader 
                    companyId={companyId}
                    onSuccess={() => {
                      queryClient.invalidateQueries({ queryKey: ['financial-overview', companyId] })
                      queryClient.invalidateQueries({ queryKey: ['financial-documents', companyId] })
                    }}
                  />
                </div>
              </Card>

              <Card className="p-4">
                <div className="text-center space-y-2">
                  <Edit className="h-8 w-8 mx-auto text-orange-500" />
                  <h3 className="font-semibold">Manual Entry</h3>
                  <p className="text-sm text-muted-foreground">
                    Enter financial data manually
                  </p>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      setPrefillStatements(undefined)
                      setShowStatementsEditor(true)
                    }}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Enter Data
                  </Button>
                </div>
              </Card>
            </div>

            {/* Uploaded Documents */}
            <div className="mt-6">
              <h3 className="font-semibold mb-2">Uploaded Documents</h3>
              {documents && documents.length > 0 ? (
                <div className="space-y-2">
                  {documents.slice(0,5).map((doc: any, idx: number) => (
                    <div key={idx} className="flex justify-between items-center border rounded p-2">
                      <div className="truncate">
                        <div className="font-medium truncate">{doc.filename}</div>
                        <div className="text-xs text-muted-foreground">
                          Status: {doc.parsing_status} • {new Date(doc.upload_date || doc.created_at || Date.now()).toLocaleString()}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" onClick={() => setReviewDoc(doc)}>Review</Button>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={async () => {
                            const confirmDel = window.confirm('Delete this document? You can also delete any statements parsed from it in the next step.')
                            if (!confirmDel) return
                            const also = window.confirm('Also delete financial statements parsed from this document?')
                            try {
                              await apiClient.deleteFinancialDocument(doc.id, { deleteStatements: also })
                              queryClient.invalidateQueries({ queryKey: ['financial-documents', companyId] })
                              queryClient.invalidateQueries({ queryKey: ['financial-overview', companyId] })
                            } catch (e) {
                              alert('Failed to delete document')
                            }
                          }}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">No documents uploaded yet</div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Financial Data Tabs */}
      {hasData && (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="statements">Statements</TabsTrigger>
            <TabsTrigger value="projections">Projections</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Historical Statements Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Historical Data</CardTitle>
                </CardHeader>
                <CardContent>
                  {overview?.historical_statements.length > 0 ? (
                    <div className="space-y-2">
                      {overview.historical_statements.slice(0, 3).map((stmt: any) => (
                        <div key={stmt.year} className="flex justify-between items-center">
                          <span>{stmt.year}</span>
                          <div className="text-right">
                            <div className="text-sm font-medium">
                              {stmt.revenue ? `${(stmt.revenue / 1000000).toFixed(1)}M SEK` : 'No revenue'}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {stmt.source}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-4">
                      No historical data available
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Actions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button 
                    className="w-full" 
                    onClick={() => generateProjections.mutate()}
                    disabled={generateProjections.isPending}
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    {generateProjections.isPending ? 'Generating...' : 'Generate 5-Year Projections'}
                  </Button>
                  
                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => generateAnalysis.mutate()}
                    disabled={generateAnalysis.isPending}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    {generateAnalysis.isPending ? 'Analyzing...' : 'Generate AI Analysis'}
                  </Button>

                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => {
                      setPrefillStatements(undefined)
                      setShowStatementsEditor(true)
                    }}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Financial Data
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Uploaded Documents */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Uploaded Documents</CardTitle>
              </CardHeader>
              <CardContent>
                {documents && documents.length > 0 ? (
                  <div className="space-y-2">
                    {documents.slice(0,5).map((doc: any, idx: number) => (
                      <div key={idx} className="flex justify-between items-center border rounded p-2">
                        <div className="truncate">
                          <div className="font-medium truncate">{doc.filename}</div>
                          <div className="text-xs text-muted-foreground">
                            Status: {doc.parsing_status} • {new Date(doc.upload_date || doc.created_at || Date.now()).toLocaleString()}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm" onClick={() => setReviewDoc(doc)}>Review</Button>
                          <Button 
                            variant="destructive" 
                            size="sm"
                            onClick={async () => {
                              const confirmDel = window.confirm('Delete this document? You can also delete any statements parsed from it in the next step.')
                              if (!confirmDel) return
                              const also = window.confirm('Also delete financial statements parsed from this document?')
                              try {
                                await apiClient.deleteFinancialDocument(doc.id, { deleteStatements: also })
                                queryClient.invalidateQueries({ queryKey: ['financial-documents', companyId] })
                                queryClient.invalidateQueries({ queryKey: ['financial-overview', companyId] })
                              } catch (e) {
                                alert('Failed to delete document')
                              }
                            }}
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">No uploaded documents</div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="statements">
            <FinancialStatementsEditor 
              companyId={companyId}
              existingData={overview?.historical_statements}
              onSave={() => queryClient.invalidateQueries({ queryKey: ['financial-overview', companyId] })}
            />
          </TabsContent>

          <TabsContent value="projections">
            <ProjectionsViewer 
              companyId={companyId}
              projections={overview?.projections || []}
              onGenerate={() => generateProjections.mutate()}
              isGenerating={generateProjections.isPending}
            />
          </TabsContent>

          <TabsContent value="analysis">
            <AnalysisViewer 
              companyId={companyId}
              analysis={overview?.latest_analysis}
              onGenerate={() => generateAnalysis.mutate()}
              isGenerating={generateAnalysis.isPending}
            />
          </TabsContent>
        </Tabs>
      )}

      {/* Review Document Dialog */}
      <Dialog open={!!reviewDoc} onOpenChange={(open) => !open && setReviewDoc(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Review Parsed Results</DialogTitle>
          </DialogHeader>
          {reviewDoc && (
            <div className="space-y-3">
              <div>
                <div className="font-medium">{reviewDoc.filename}</div>
                <div className="text-sm text-muted-foreground">Status: {reviewDoc.parsing_status}</div>
              </div>
              <div className="text-sm">
                <div>Statements found: {Array.isArray(reviewDoc.extracted_data?.financial_statements) ? reviewDoc.extracted_data.financial_statements.length : 0}</div>
                <div>Years: {Array.isArray(reviewDoc.extracted_data?.years_found) ? reviewDoc.extracted_data.years_found.join(', ') : '—'}</div>
                <div>Pages: {reviewDoc.extracted_data?.raw_content?.page_count ?? '—'} • Tables: {reviewDoc.extracted_data?.raw_content?.table_count ?? '—'}</div>
              </div>
              {reviewDoc.extracted_data?.raw_content?.text_preview && (
                <div className="bg-gray-50 rounded p-2 text-xs max-h-40 overflow-auto">
                  {reviewDoc.extracted_data.raw_content.text_preview}
                </div>
              )}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setReviewDoc(null)}>Close</Button>
                {Array.isArray(reviewDoc.extracted_data?.financial_statements) && reviewDoc.extracted_data.financial_statements.length > 0 ? (
                  <Button onClick={() => {
                    setPrefillStatements(reviewDoc.extracted_data.financial_statements)
                    setShowStatementsEditor(true)
                    setReviewDoc(null)
                  }}>
                    Load into Editor
                  </Button>
                ) : (
                  <Button onClick={() => {
                    setPrefillStatements(undefined)
                    setShowStatementsEditor(true)
                    setReviewDoc(null)
                  }}>
                    Open Editor (manual)
                  </Button>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Statements Editor Dialog when prefilling parsed data */}
      <Dialog open={showStatementsEditor} onOpenChange={(open) => { setShowStatementsEditor(open); if (!open) setPrefillStatements(undefined) }}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Financial Statements Editor</DialogTitle>
          </DialogHeader>
          <FinancialStatementsEditor 
            companyId={companyId}
            existingData={prefillStatements || overview?.historical_statements}
            onSave={() => {
              setShowStatementsEditor(false)
              setPrefillStatements(undefined)
              queryClient.invalidateQueries({ queryKey: ['financial-overview', companyId] })
              queryClient.invalidateQueries({ queryKey: ['financial-documents', companyId] })
            }}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
