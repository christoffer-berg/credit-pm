import { useState, useEffect } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Wand2, Save, Eye, EyeOff } from 'lucide-react'

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

interface SimpleSectionEditorProps {
  section: PMSection
  onRegenerate: () => void
  isRegenerating: boolean
  onSectionUpdate?: (section: PMSection) => void
}

export function SimpleSectionEditor({ 
  section, 
  onRegenerate, 
  isRegenerating, 
  onSectionUpdate 
}: SimpleSectionEditorProps) {
  const [userContent, setUserContent] = useState(section.user_content || section.ai_content || '')
  const [showAiContent, setShowAiContent] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')

  useEffect(() => {
    const currentContent = section.user_content || section.ai_content || ''
    setUserContent(currentContent)
    setHasChanges(false)
    setSaveStatus('idle')
  }, [section])

  const handleContentChange = (value: string) => {
    setUserContent(value)
    setHasChanges(value !== (section.user_content || section.ai_content || ''))
    setSaveStatus('idle')
  }

  const handleSave = async () => {
    setIsSaving(true)
    setSaveStatus('idle')
    
    try {
      const response = await fetch(`/api/v1/sections/${section.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_content: userContent }),
      })
      
      if (!response.ok) throw new Error('Failed to update section')
      
      const updatedSection = await response.json()
      setHasChanges(false)
      setSaveStatus('success')
      
      // Call the update callback if provided
      if (onSectionUpdate) {
        onSectionUpdate(updatedSection)
      }
      
      // Clear success message after 3 seconds
      setTimeout(() => setSaveStatus('idle'), 3000)
      
    } catch (error) {
      console.error('Save failed:', error)
      setSaveStatus('error')
    } finally {
      setIsSaving(false)
    }
  }

  const handleUseAiContent = () => {
    if (section.ai_content) {
      setUserContent(section.ai_content)
      setHasChanges(section.ai_content !== (section.user_content || ''))
      setSaveStatus('idle')
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
                disabled={isSaving}
              >
                <Save className="w-4 h-4 mr-1" />
                {isSaving ? 'Saving...' : 'Save'}
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

      {/* Status Messages */}
      {saveStatus === 'error' && (
        <div className="text-red-600 text-sm">
          Failed to save changes. Please try again.
        </div>
      )}
      
      {saveStatus === 'success' && (
        <div className="text-green-600 text-sm">
          Changes saved successfully.
        </div>
      )}
    </div>
  )
}