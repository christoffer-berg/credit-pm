'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSupabaseClient } from '@supabase/auth-helpers-react'
import { PMCaseEditor } from '@/components/cases/pm-case-editor'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Download, FileText } from 'lucide-react'
import Link from 'next/link'
import { useParams } from 'next/navigation'

export default function CaseDetailPage() {
  const params = useParams()
  const caseId = params.id as string
  const supabase = useSupabaseClient()

  const { data: pmCase, isLoading: caseLoading } = useQuery({
    queryKey: ['case', caseId],
    queryFn: async () => {
      const session = await supabase.auth.getSession()
      const response = await fetch(`/api/v1/cases/${caseId}`, {
        headers: {
          'Authorization': `Bearer ${session.data.session?.access_token}`,
        },
      })
      if (!response.ok) throw new Error('Failed to fetch case')
      return response.json()
    },
  })

  const { data: sections, isLoading: sectionsLoading } = useQuery({
    queryKey: ['sections', caseId],
    queryFn: async () => {
      const session = await supabase.auth.getSession()
      const response = await fetch(`/api/v1/sections/${caseId}`, {
        headers: {
          'Authorization': `Bearer ${session.data.session?.access_token}`,
        },
      })
      if (!response.ok) throw new Error('Failed to fetch sections')
      return response.json()
    },
  })

  const handleExport = async (format: 'word' | 'pdf') => {
    try {
      const session = await supabase.auth.getSession()
      const response = await fetch(`/api/v1/export/${caseId}/${format}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.data.session?.access_token}`,
        },
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `credit_pm_${pmCase?.title?.replace(/\s+/g, '_') || 'document'}.${format === 'word' ? 'docx' : 'pdf'}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  if (caseLoading || sectionsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div>Loading...</div>
      </div>
    )
  }

  if (!pmCase) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card>
          <CardHeader>
            <CardTitle>Case Not Found</CardTitle>
            <CardDescription>The requested credit memo could not be found.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <Button variant="outline" asChild>
                <Link href="/">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {pmCase.title}
                </h1>
                <p className="text-sm text-gray-500">
                  Version {pmCase.version} • {pmCase.status}
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" onClick={() => handleExport('word')}>
                <FileText className="w-4 h-4 mr-2" />
                Export Word
              </Button>
              <Button variant="outline" onClick={() => handleExport('pdf')}>
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <PMCaseEditor caseId={caseId} pmCase={pmCase} sections={sections || []} />
      </main>
    </div>
  )
}