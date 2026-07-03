import { useAuth } from "@/lib/auth";

export function useApoemaAuthAdapter() {
  const { bootError, isAdmin, loading, logout, profile, session, signOut, token, user } = useAuth();

  return {
    bootError,
    isAdmin,
    loading,
    profile,
    session,
    signOut,
    token,
    user,
    logout,
  };
}
