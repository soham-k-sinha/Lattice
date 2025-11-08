"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { api } from "@/lib/api"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("alice@demo.com")
  const [password, setPassword] = useState("password123")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    console.log('🔐 Login attempt:', email)

    try {
      console.log('📡 Calling backend login API...')
      const data = await api.login(email, password)
      console.log('✅ Login response received:', data)
      
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token)
        console.log('✅ Token saved to localStorage')
        
        // Verify token was saved
        const savedToken = localStorage.getItem("access_token")
        console.log('🔍 Verified token in localStorage:', savedToken ? 'YES' : 'NO')
        
        console.log('🔀 Redirecting to /chat/1...')
        router.push("/onboarding")
      } else {
        console.error('❌ No access_token in response:', data)
        setError("Invalid response from server")
      }
    } catch (err: any) {
      console.error('❌ Login error:', err)
      setError(err.message || "Login failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
      {/* Animated mesh background */}
      <div className="absolute inset-0 overflow-hidden opacity-30">
        <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="lattice" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
              <motion.circle
                cx="50"
                cy="50"
                r="1"
                fill="currentColor"
                className="text-accent"
                animate={{
                  r: [1, 2, 1],
                  opacity: [0.3, 0.6, 0.3],
                }}
                transition={{
                  duration: 4,
                  repeat: Number.POSITIVE_INFINITY,
                  ease: "easeInOut",
                }}
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#lattice)" />
        </svg>
      </div>

      {/* Logo */}
      <motion.div
        className="absolute top-8 left-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Link href="/">
          <span className="font-mono text-xl font-semibold tracking-tight cursor-pointer">Lattice.</span>
        </Link>
      </motion.div>

      {/* Login form */}
      <motion.div
        className="relative z-10 w-full max-w-md mx-auto px-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
          <h1 className="text-3xl font-semibold mb-2">Welcome back</h1>
          <p className="text-muted-foreground mb-6">Sign in to your Lattice account</p>

          {error && (
            <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm">
            <p className="text-muted-foreground">
              Don't have an account?{" "}
              <Link href="/signup" className="text-accent hover:underline">
                Sign up
              </Link>
            </p>
          </div>

          {/* Demo credentials hint */}
          <div className="mt-6 p-4 bg-muted/50 rounded-lg">
            <p className="text-xs text-muted-foreground font-medium mb-2">Demo Credentials:</p>
            <p className="text-xs text-muted-foreground">Email: alice@demo.com</p>
            <p className="text-xs text-muted-foreground">Password: password123</p>
          </div>
        </div>
      </motion.div>
    </main>
  )
}

