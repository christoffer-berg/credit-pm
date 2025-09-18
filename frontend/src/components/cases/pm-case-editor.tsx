'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { SectionEditor } from './section-editor'
import { FinancialDataManager } from '@/components/financials/financial-data-manager'
import { PMCase, PMSection } from '@/types'
import { Wand2, Plus, BarChart3 } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface PMCaseEditorProps {
  caseId: string
  pmCase: PMCase
  sections: PMSection[]
}

const SECTION_TYPES = [
  { type: 'purpose', title: 'Purpose', description: 'Objective of the credit analysis' },
  { type: 'business_description', title: 'Business Description', description: 'Company overview and operations' },
  { type: 'market_analysis', title: 'Market Analysis', description: 'Industry and competitive landscape' },
  { type: 'financial_analysis', title: 'Financial Analysis', description: 'Financial performance and forecasts' },
  { type: 'credit_analysis', title: 'Credit Analysis', description: 'Risk assessment and credit evaluation' },
  { type: 'credit_proposal', title: 'Credit Proposal', description: 'Recommendations and terms' },
]

export function PMCaseEditor({ caseId, pmCase, sections }: PMCaseEditorProps) {
  const [generatingSection, setGeneratingSection] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('sections')
  const queryClient = useQueryClient()

  const generateSectionMutation = useMutation({
    mutationFn: async (sectionType: string) => {
      const { apiClient } = await import('@/lib/api-client')
      return apiClient.generateSection(caseId, sectionType)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sections', caseId] })
      setGeneratingSection(null)
    },
    onError: (error) => {
      console.error('Generation failed:', error)
      setGeneratingSection(null)
    }
  })

  const handleGenerateSection = (sectionType: string) => {
    setGeneratingSection(sectionType)
    generateSectionMutation.mutate(sectionType)
  }

  const getSectionData = (sectionType: string) => {
    return sections.find(section => section.section_type === sectionType)
  }

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab}>
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="sections">PM Sections</TabsTrigger>
        <TabsTrigger value="financials">Financial Data</TabsTrigger>
      </TabsList>

      <TabsContent value="sections" className="space-y-6 mt-6">
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
                      disabled={isGenerating}
                    >
                      <Wand2 className="w-4 h-4 mr-1" />
                      {isGenerating ? 'Generating...' : 'Generate with AI'}
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {sectionData ? (
                  <SectionEditor
                    section={sectionData}
                    onRegenerate={() => handleGenerateSection(sectionType.type)}
                    isRegenerating={isGenerating}
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
      </TabsContent>

      <TabsContent value="financials" className="mt-6">
        <FinancialDataManager
          companyId={pmCase.company_id}
          companyName={pmCase.company?.name || ''}
          orgNumber={pmCase.company?.organization_number || ''}
        />
      </TabsContent>
    </Tabs>
  )
}
