import { createServerClient } from '@/lib/supabase-server'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = createServerClient()
    
    const { data: pmCase, error } = await supabase
      .from('pm_cases')
      .select(`
        *,
        company:companies(*)
      `)
      .eq('id', params.id)
      .single()
    
    if (error) {
      console.error('Supabase error:', error)
      if (error.code === 'PGRST116') {
        return NextResponse.json(
          { error: 'Case not found' },
          { status: 404 }
        )
      }
      return NextResponse.json(
        { error: 'Failed to fetch case' },
        { status: 500 }
      )
    }
    
    return NextResponse.json(pmCase)
  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}