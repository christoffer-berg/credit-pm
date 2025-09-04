'use client'

import { useState } from 'react'
import { format } from 'date-fns'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { PMCase } from '@/types'
import { FileText, Download, Edit, Trash2 } from 'lucide-react'
import Link from 'next/link'

interface CaseListProps {
  cases: PMCase[]
  onRefetch: () => void
}

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

export function CaseList({ cases, onRefetch }: CaseListProps) {
  const [deletingCases, setDeletingCases] = useState<Set<string>>(new Set())

  const handleDelete = async (caseId: string, caseTitle: string) => {
    if (!confirm(`Are you sure you want to delete "${caseTitle}"? This action cannot be undone.`)) {
      return
    }

    setDeletingCases(prev => new Set(prev.add(caseId)))

    try {
      const response = await fetch(`/api/v1/cases/${caseId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      })

      if (response.ok) {
        onRefetch() // Refresh the case list
      } else {
        throw new Error(`Failed to delete case: ${response.status}`)
      }
    } catch (err) {
      console.error('Error deleting case:', err)
      alert('Failed to delete case. Please try again.')
    } finally {
      setDeletingCases(prev => {
        const newSet = new Set(prev)
        newSet.delete(caseId)
        return newSet
      })
    }
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {cases.map((pmCase) => (
        <Card key={pmCase.id} className="hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="flex justify-between items-start">
              <CardTitle className="text-lg">{pmCase.title}</CardTitle>
              <Badge className={statusColors[pmCase.status]}>
                {statusLabels[pmCase.status]}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-gray-600">
              <div>Version: {pmCase.version}</div>
              <div>Created: {format(new Date(pmCase.created_at), 'MMM d, yyyy')}</div>
              <div>Updated: {format(new Date(pmCase.updated_at), 'MMM d, yyyy')}</div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button asChild size="sm" className="flex-1">
                <Link href={`/cases/${pmCase.id}`}>
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </Link>
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4" />
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => handleDelete(pmCase.id, pmCase.title)}
                disabled={deletingCases.has(pmCase.id)}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}