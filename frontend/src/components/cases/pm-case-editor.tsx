'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSupabaseClient } from '@supabase/auth-helpers-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { SectionEditor } from './section-editor'
import { PMCase, PMSection } from '@/types'
import { Wand2, Plus } from 'lucide-react'

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
  const supabase = useSupabaseClient()
  const queryClient = useQueryClient()

  const generateSectionMutation = useMutation({
    mutationFn: async (sectionType: string) => {
      const session = await supabase.auth.getSession()
      const response = await fetch(`/api/v1/sections/${caseId}/generate?section_type=${sectionType}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.data.session?.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      if (!response.ok) throw new Error('Failed to generate section')
      return response.json()
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
    </div>
  )
}