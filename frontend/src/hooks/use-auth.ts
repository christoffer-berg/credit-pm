import { useSupabaseClient, useUser, useSession } from '@supabase/auth-helpers-react'
import { useRouter } from 'next/navigation'

export function useAuth() {
  const supabase = useSupabaseClient()
  const user = useUser()
  const session = useSession()
  const router = useRouter()

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    
    if (error) throw error
    
    return data
  }

  const signUp = async (email: string, password: string, metadata?: Record<string, any>) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata,
      },
    })
    
    if (error) throw error
    
    return data
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    
    router.push('/')
  }

  const resetPassword = async (email: string) => {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    })
    
    if (error) throw error
    
    return data
  }

  const updatePassword = async (password: string) => {
    const { data, error } = await supabase.auth.updateUser({
      password,
    })
    
    if (error) throw error
    
    return data
  }

  return {
    user,
    session,
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    isAuthenticated: !!user,
    isLoading: !user && !session, // Loading if we don't have user data yet
  }
}