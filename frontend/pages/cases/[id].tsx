import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { SimpleSectionEditor } from '@/components/cases/simple-section-editor'
import { CompanyInfo } from '@/components/cases/company-info'
import { ArrowLeft, Wand2, Plus, RefreshCw } from 'lucide-react'
import Link from 'next/link'

interface PMCase {
  id: string
  title: string
  status: string
  version: number
  created_at: string
  updated_at: string
  company_id: string
}

interface PMSection {
  id: string
  case_id: string
  section_type: string
  title: string
  ai_content: string | null
  user_content: string | null
  version: number
  created_at: string
  updated_at: string
}

interface Company {
  id: string
  organization_number: string
  name: string
  business_description?: string
  industry_code?: string
  website?: string
  email?: string
  phone?: string
  address?: string
  contact_person?: string
}

const SECTION_TYPES = [
  { type: 'purpose', title: 'Purpose', description: 'Objective of the credit analysis' },
  { type: 'market_analysis', title: 'Market Analysis', description: 'Industry and competitive landscape' },
  { type: 'financial_analysis', title: 'Financial Analysis', description: 'Financial performance and forecasts' },
  { type: 'credit_analysis', title: 'Credit Analysis', description: 'Risk assessment and credit evaluation' },
  { type: 'credit_proposal', title: 'Credit Proposal', description: 'Recommendations and terms' },
]

const statusColors = {
  draft: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  exported: 'bg-purple-100 text-purple-800',
}

const statusLabels = {
  draft: 'Draft',
  in_progress: 'In Progress',
  completed: 'Completed',
  exported: 'Exported',
}

export default function CaseDetailPage() {
  const router = useRouter()
  const { id } = router.query
  
  const [pmCase, setPmCase] = useState<PMCase | null>(null)
  const [company, setCompany] = useState<Company | null>(null)
  const [sections, setSections] = useState<PMSection[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generatingSection, setGeneratingSection] = useState<string | null>(null)
  const [generatingComplete, setGeneratingComplete] = useState(false)

  const fetchCase = async () => {
    if (!id) return
    
    try {
      const response = await fetch(`/api/v1/cases/${id}`)
      if (!response.ok) throw new Error(`Failed to fetch case: ${response.status}`)
      const data = await response.json()
      setPmCase(data)
      
      // Fetch company data if we have a company_id
      if (data.company_id) {
        await fetchCompany(data.company_id)
      }
    } catch (err: any) {
      setError(err.message)
    }
  }

  const fetchCompany = async (companyId: string) => {
    try {
      const response = await fetch(`/api/v1/companies/${companyId}`)
      if (!response.ok) throw new Error(`Failed to fetch company: ${response.status}`)
      const data = await response.json()
      setCompany(data)
    } catch (err: any) {
      console.error('Error fetching company:', err)
      // Don't set error here as company data is optional for UI display
    }
  }

  const fetchSections = async () => {
    if (!id) return
    
    try {
      const response = await fetch(`/api/v1/sections/${id}`)
      if (!response.ok) throw new Error(`Failed to fetch sections: ${response.status}`)
      const data = await response.json()
      setSections(data)
    } catch (err: any) {
      console.error('Error fetching sections:', err)
      setSections([])
    }
  }

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    
    await Promise.all([fetchCase(), fetchSections()])
    setIsLoading(false)
  }

  useEffect(() => {
    if (id) {
      fetchData()
    }
  }, [id])

  const handleGenerateSection = async (sectionType: string) => {
    if (!id) return
    
    setGeneratingSection(sectionType)
    try {
      const response = await fetch(`/api/v1/sections/${id}/generate?section_type=${sectionType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) throw new Error('Failed to generate section')
      
      // Refresh sections after generation
      await fetchSections()
    } catch (err: any) {
      console.error('Generation failed:', err)
      setError(`Failed to generate ${sectionType}: ${err.message}`)
    } finally {
      setGeneratingSection(null)
    }
  }

  const handleGenerateComplete = async () => {
    if (!id) return
    
    setGeneratingComplete(true)
    try {
      const response = await fetch(`/api/v1/cases/${id}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) throw new Error('Failed to generate complete PM')
      
      // Refresh both case and sections after generation
      await fetchData()
    } catch (err: any) {
      console.error('Complete generation failed:', err)
      setError(`Failed to generate complete PM: ${err.message}`)
    } finally {
      setGeneratingComplete(false)
    }
  }

  const getSectionData = (sectionType: string) => {
    return sections.find(section => section.section_type === sectionType)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">Loading case...</p>
        </div>
      </div>
    )
  }

  if (error && !pmCase) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center py-6">
              <Button asChild variant="ghost" size="sm" className="mr-4">
                <Link href="/">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <h1 className="text-3xl font-bold text-gray-900">Error</h1>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Card>
            <CardHeader>
              <CardTitle>Error Loading Case</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-600 mb-4">{error}</p>
              <Button onClick={fetchData}>Try Again</Button>
            </CardContent>
          </Card>
        </main>
      </div>
    )
  }

  if (!pmCase) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Case not found</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center">
              <Button asChild variant="ghost" size="sm" className="mr-4">
                <Link href="/">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{pmCase.title}</h1>
                <div className="flex items-center space-x-4 mt-2">
                  <Badge className={statusColors[pmCase.status as keyof typeof statusColors]}>
                    {statusLabels[pmCase.status as keyof typeof statusLabels]}
                  </Badge>
                  <span className="text-sm text-gray-500">Version {pmCase.version}</span>
                </div>
              </div>
            </div>
            <Button 
              onClick={handleGenerateComplete}
              disabled={generatingComplete}
              size="lg"
            >
              <Wand2 className="w-4 h-4 mr-2" />
              {generatingComplete ? 'Generating...' : 'Generate Complete PM'}
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <Card className="mb-6 border-red-200">
              <CardContent className="pt-6">
                <p className="text-red-600">{error}</p>
                <Button 
                  onClick={() => setError(null)} 
                  variant="outline" 
                  size="sm" 
                  className="mt-2"
                >
                  Dismiss
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Company Information Section */}
          {company && (
            <CompanyInfo
              company={company}
              onUpdate={(updatedCompany) => setCompany(updatedCompany)}
            />
          )}

          <div className="space-y-6">
            {SECTION_TYPES.map((sectionType) => {
              const sectionData = getSectionData(sectionType.type)
              const isGenerating = generatingSection === sectionType.type

              return (
                <Card key={sectionType.type} className="w-full">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {sectionType.title}
                          {sectionData && (
                            <Badge variant="outline" className="text-xs">
                              v{sectionData.version}
                            </Badge>
                          )}
                        </CardTitle>
                        <CardDescription>{sectionType.description}</CardDescription>
                      </div>
                      {!sectionData && (
                        <Button
                          size="sm"
                          onClick={() => handleGenerateSection(sectionType.type)}
                          disabled={isGenerating || generatingComplete}
                        >
                          <Wand2 className="w-4 h-4 mr-1" />
                          {isGenerating ? 'Generating...' : 'Generate with AI'}
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    {sectionData ? (
                      <SimpleSectionEditor
                        section={sectionData}
                        onRegenerate={() => handleGenerateSection(sectionType.type)}
                        isRegenerating={isGenerating}
                        onSectionUpdate={(updatedSection) => {
                          // Update the sections state with the updated section
                          setSections(prev => 
                            prev.map(s => s.id === updatedSection.id ? updatedSection : s)
                          )
                        }}
                      />
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <Plus className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                        <p>No content generated yet</p>
                        <p className="text-sm">Click "Generate with AI" to create this section</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </main>
    </div>
  )
}