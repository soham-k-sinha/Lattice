"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ArrowLeft, CheckCircle2, Trash2 } from "lucide-react"
import Link from "next/link"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api, type Account } from "@/lib/api"

export default function AccountsPage() {
  const router = useRouter()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<number | null>(null)

  useEffect(() => {
    loadAccounts()
  }, [])

  const loadAccounts = async () => {
    try {
      setLoading(true)
      const data = await api.getAccounts()
      setAccounts(data.accounts || [])
    } catch (error) {
      console.error("Failed to load accounts:", error)
      if (error instanceof Error && error.message.includes("401")) {
        router.push("/login")
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteAccount = async (accountId: number) => {
    if (!confirm("Are you sure you want to unlink this account?")) return

    try {
      setDeleting(accountId)
      await api.deleteAccount(accountId)
      // Reload accounts after deletion
      await loadAccounts()
    } catch (error) {
      console.error("Failed to delete account:", error)
      alert("Failed to unlink account. Please try again.")
    } finally {
      setDeleting(null)
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading accounts...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-8">
          <Link href="/chat/1">
            <Button variant="ghost" className="rounded-full mb-4" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Chat
            </Button>
          </Link>
          <h1 className="text-3xl font-semibold mb-2">Linked Accounts</h1>
          <p className="text-muted-foreground">Manage your connected financial institutions</p>
        </div>

        <div className="space-y-4 mb-8">
          {accounts.map((account, index) => (
            <motion.div
              key={account.id}
              className="bg-card border border-border rounded-xl p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold mb-1">{account.account_name}</h3>
                  <p className="text-sm text-muted-foreground">{account.institution}</p>
                  {account.balance !== undefined && (
                  <p className="text-xs text-muted-foreground mt-1">
                      Balance: ${account.balance.toFixed(2)} {account.currency || 'USD'}
                  </p>
                  )}
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="rounded-full text-destructive"
                  onClick={() => handleDeleteAccount(account.id)}
                  disabled={deleting === account.id}
                >
                  {deleting === account.id ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-destructive"></div>
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                </Button>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium mb-2">Permissions</p>
                {account.permissions && Object.entries(account.permissions).map(([key, value]) => (
                  value && (
                    <div key={key} className="flex items-center gap-2 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-accent" />
                      <span className="text-muted-foreground capitalize">{key.replace(/_/g, " ")}</span>
                    </div>
                  )
                ))}
              </div>

              {account.last_synced && (
              <div className="mt-4 pt-4 border-t border-border">
                <p className="text-xs text-muted-foreground">
                  Last synced: {new Date(account.last_synced).toLocaleString()}
                </p>
              </div>
              )}
            </motion.div>
          ))}
        </div>

        {accounts.length === 0 && !loading && (
          <motion.div
            className="text-center py-16"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="w-16 h-16 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
              <CheckCircle2 className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No accounts linked</h3>
            <p className="text-muted-foreground mb-6">Connect your financial accounts to get started</p>
          </motion.div>
        )}

        <motion.div
          className="bg-accent/10 border border-accent/20 rounded-xl p-6 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <p className="text-sm font-medium mb-2">🏖️ Sandbox Mode Active</p>
          <p className="text-sm text-muted-foreground">
            Using demo data for testing. Knot integration will be available soon.
          </p>
        </motion.div>
      </div>
    </main>
  )
}
