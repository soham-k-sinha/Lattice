"use client"

import { motion } from "framer-motion"
import { AppNavigation } from "@/components/app-navigation"
import { Button } from "@/components/ui/button"
import { User, CreditCard, Bell, Shield, LogOut, Check } from "lucide-react"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"

export default function SettingsPage() {
  const router = useRouter()
  const [settings, setSettings] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)

  useEffect(() => {
    loadSettings()
    loadUser()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const data = await api.getSettings()
      setSettings(data)
    } catch (error) {
      console.error("Failed to load settings:", error)
      if (error instanceof Error && error.message.includes("401")) {
        router.push("/login")
      }
    } finally {
      setLoading(false)
    }
  }

  const loadUser = async () => {
    try {
      const user = await api.getCurrentUser()
      setCurrentUser(user)
    } catch (error) {
      console.error("Failed to load user:", error)
    }
  }

  const handleLogout = async () => {
    await api.logout()
    router.push("/login")
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-background">
        <AppNavigation />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading settings...</p>
          </div>
        </div>
      </div>
    )
  }

  const settingSections = [
    {
      title: "Account",
      icon: User,
      items: [
        { 
          label: "Profile", 
          description: currentUser ? `${currentUser.name} (${currentUser.email})` : "Manage your personal information" 
        },
        { label: "Email & Password", description: "Update your login credentials" },
      ],
    },
    {
      title: "Connected Accounts",
      icon: CreditCard,
      items: [
        { 
          label: "Knot Integration", 
          description: "Manage connected financial accounts", 
          status: settings?.connected_accounts?.total > 0 ? "Connected" : "Not Connected"
        },
        { label: "Payment Methods", description: `${settings?.connected_accounts?.total || 0} accounts linked` },
      ],
    },
    {
      title: "Preferences",
      icon: Bell,
      items: [
        { 
          label: "Notifications", 
          description: settings?.preferences?.notifications?.email ? "Email enabled" : "Email disabled" 
        },
        { 
          label: "AI Insights", 
          description: settings?.preferences?.ai?.enabled ? "Enabled" : "Disabled" 
        },
      ],
    },
    {
      title: "Security",
      icon: Shield,
      items: [
        { 
          label: "Privacy", 
          description: settings?.preferences?.privacy?.data_collection ? "Data collection enabled" : "Limited data" 
        },
        { 
          label: "Two-factor Auth", 
          description: settings?.security?.["2fa_enabled"] ? "Enabled" : "Not enabled" 
        },
      ],
    },
  ]

  return (
    <div className="flex h-screen bg-background">
      <AppNavigation />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-semibold mb-2">Settings</h1>
            <p className="text-muted-foreground">Manage your account and preferences</p>
          </div>

          {/* User info card */}
          {currentUser && (
            <motion.div
              className="mb-8 p-6 rounded-xl border border-border bg-card"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center">
                  <User className="w-8 h-8 text-accent" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">{currentUser.name}</h2>
                  <p className="text-sm text-muted-foreground">{currentUser.email}</p>
                  <div className="mt-1 flex items-center gap-1.5 text-xs text-accent">
                    <Check className="w-3 h-3" />
                    <span>Verified account</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Settings sections */}
          <div className="space-y-8">
            {settingSections.map((section, sectionIndex) => (
              <motion.div
                key={section.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: sectionIndex * 0.1 + 0.1 }}
              >
                <div className="flex items-center gap-2 mb-4">
                  <section.icon className="w-4 h-4 text-muted-foreground" />
                  <h2 className="font-semibold">{section.title}</h2>
                </div>

                <div className="space-y-2">
                  {section.items.map((item) => (
                    <motion.button
                      key={item.label}
                      className="w-full text-left p-4 rounded-xl border border-border bg-card hover:border-accent/50 transition-colors"
                      whileHover={{ x: 4 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium mb-0.5">{item.label}</p>
                          <p className="text-sm text-muted-foreground">{item.description}</p>
                        </div>
                        {item.status && (
                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            item.status.includes("Connected") || item.status.includes("Enabled")
                              ? "bg-accent/10 text-accent"
                              : "bg-muted text-muted-foreground"
                          }`}>
                            {item.status}
                          </span>
                        )}
                      </div>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>

          {/* Sign out */}
          <motion.div
            className="mt-8 pt-8 border-t border-border"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <Button
              variant="outline"
              className="rounded-full gap-2 text-destructive hover:text-destructive bg-transparent"
              onClick={handleLogout}
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </Button>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
