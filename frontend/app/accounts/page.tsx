"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ArrowLeft, CheckCircle2, Trash2 } from "lucide-react"
import Link from "next/link"

const accounts = [
  {
    id: 1,
    name: "Chase Checking",
    institution: "Chase",
    permissions: ["Read transactions", "Payments"],
  },
  {
    id: 2,
    name: "Discover It",
    institution: "Discover",
    permissions: ["Read transactions"],
  },
]

export default function AccountsPage() {
  return (
    <main className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-8">
          <Link href="/chat/main">
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
                  <h3 className="font-semibold mb-1">{account.name}</h3>
                  <p className="text-sm text-muted-foreground">{account.institution}</p>
                </div>
                <Button variant="ghost" size="icon" className="rounded-full text-destructive">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium mb-2">Permissions</p>
                {account.permissions.map((permission) => (
                  <div key={permission} className="flex items-center gap-2 text-sm">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    <span className="text-muted-foreground">{permission}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          className="bg-accent/10 border border-accent/20 rounded-xl p-6 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <p className="text-sm font-medium mb-2">🏖️ Sandbox active</p>
          <p className="text-sm text-muted-foreground">
            Using demo data for testing. Connect real accounts in production.
          </p>
        </motion.div>
      </div>
    </main>
  )
}
