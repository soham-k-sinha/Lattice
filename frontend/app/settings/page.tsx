"use client"

import { motion } from "framer-motion"
import { AppNavigation } from "@/components/app-navigation"
import { Button } from "@/components/ui/button"
import { User, CreditCard, Bell, Shield, LogOut } from "lucide-react"

const settingSections = [
  {
    title: "Account",
    icon: User,
    items: [
      { label: "Profile", description: "Manage your personal information" },
      { label: "Email & Password", description: "Update your login credentials" },
    ],
  },
  {
    title: "Connected Accounts",
    icon: CreditCard,
    items: [
      { label: "Knot Integration", description: "Manage connected financial accounts", status: "Connected" },
      { label: "Payment Methods", description: "View and manage your cards" },
    ],
  },
  {
    title: "Preferences",
    icon: Bell,
    items: [
      { label: "Notifications", description: "Manage alerts and updates" },
      { label: "AI Insights", description: "Control AI recommendation frequency" },
    ],
  },
  {
    title: "Security",
    icon: Shield,
    items: [
      { label: "Privacy", description: "Control your data and privacy settings" },
      { label: "Two-factor Auth", description: "Add extra security to your account" },
    ],
  },
]

export default function SettingsPage() {
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

          {/* Settings sections */}
          <div className="space-y-8">
            {settingSections.map((section, sectionIndex) => (
              <motion.div
                key={section.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: sectionIndex * 0.1 }}
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
                          <span className="text-xs px-2 py-1 rounded-full bg-accent/10 text-accent font-medium">
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
