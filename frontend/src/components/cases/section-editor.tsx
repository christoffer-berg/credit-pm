'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PMSection, UpdateSectionRequest } from '@/types'
import { Wand2, Save, Eye, EyeOff } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SectionEditorProps {
  section: PMSection
  onRegenerate: () => void
  isRegenerating: boolean
}

export function SectionEditor({ section, onRegenerate, isRegenerating }: SectionEditorProps) {
  const [userContent, setUserContent] = useState(section.user_content || section.ai_content || '')
  const [showAiContent, setShowAiContent] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const queryClient = useQueryClient()

  useEffect(() => {
    const currentContent = section.user_content || section.ai_content || ''
    setUserContent(currentContent)
    setHasChanges(false)
  }, [section])

  const updateSectionMutation = useMutation({
    mutationFn: async (data: UpdateSectionRequest) => {
      const { apiClient } = await import('@/lib/api-client')
      return apiClient.updateSection(section.id, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sections', section.case_id] })
      setHasChanges(false)
    },
  })

  const handleContentChange = (value: string) => {
    setUserContent(value)
    setHasChanges(value !== (section.user_content || section.ai_content || ''))
  }

  const handleSave = () => {
    updateSectionMutation.mutate({ user_content: userContent })
  }

  const handleUseAiContent = () => {
    if (section.ai_content) {
      setUserContent(section.ai_content)
      setHasChanges(section.ai_content !== (section.user_content || ''))
    }
  }

  const displayContent = userContent || section.ai_content || ''
  const hasAiContent = !!section.ai_content
  const hasUserContent = !!section.user_content

  return (
    <div className="space-y-4">
      {/* Content Editor */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Content</span>
            {hasUserContent && (
              <Badge variant="outline" className="text-xs">
                Modified
              </Badge>
            )}
            {hasAiContent && !hasUserContent && (
              <Badge variant="secondary" className="text-xs">
                AI Generated
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {hasAiContent && hasUserContent && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAiContent(!showAiContent)}
              >
                {showAiContent ? <EyeOff className="w-4 h-4 mr-1" /> : <Eye className="w-4 h-4 mr-1" />}
                {showAiContent ? 'Hide' : 'Show'} AI Version
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={onRegenerate}
              disabled={isRegenerating}
            >
              <Wand2 className="w-4 h-4 mr-1" />
              {isRegenerating ? 'Regenerating...' : 'Regenerate'}
            </Button>
            {hasChanges && (
              <Button
                size="sm"
                onClick={handleSave}
                disabled={updateSectionMutation.isPending}
              >
                <Save className="w-4 h-4 mr-1" />
                {updateSectionMutation.isPending ? 'Saving...' : 'Save'}
              </Button>
            )}
          </div>
        </div>
        <Textarea
          value={displayContent}
          onChange={(e) => handleContentChange(e.target.value)}
          placeholder="Enter content for this section..."
          className="min-h-[200px] resize-y"
          disabled={isRegenerating}
        />
      </div>

      {/* AI Content Comparison */}
      {showAiContent && section.ai_content && hasUserContent && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm">Original AI Content</CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={handleUseAiContent}
              >
                Use This Version
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded border">
              {section.ai_content}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Status */}
      {updateSectionMutation.isError && (
        <div className="text-red-600 text-sm">
          Failed to save changes. Please try again.
        </div>
      )}
      
      {updateSectionMutation.isSuccess && !hasChanges && (
        <div className="text-green-600 text-sm">
          Changes saved successfully.
        </div>
      )}
    </div>
  )
}
