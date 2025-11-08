"use client"

import { motion } from "framer-motion"
import { AppNavigation } from "@/components/app-navigation"
import { TrendingUp, TrendingDown, CreditCard, Users, Sparkles, AlertCircle } from "lucide-react"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api, type Insight } from "@/lib/api"

const colorMap: Record<string, { bg: string; text: string }> = {
  optimization: { bg: "bg-teal-500/10", text: "text-teal-500" },
  spending: { bg: "bg-violet-500/10", text: "text-violet-500" },
  rewards: { bg: "bg-blue-500/10", text: "text-blue-500" },
  warning: { bg: "bg-amber-500/10", text: "text-amber-500" },
  success: { bg: "bg-green-500/10", text: "text-green-500" },
}

const iconMap: Record<string, any> = {
  optimization: CreditCard,
  spending: Users,
  rewards: Sparkles,
  warning: AlertCircle,
  success: TrendingUp,
}

export default function InsightsPage() {
  const router = useRouter()
  const [insights, setInsights] = useState<Insight[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInsights()
  }, [])

  const loadInsights = async () => {
    try {
      setLoading(true)
      const [insightsData, summaryData] = await Promise.all([
        api.getInsights(),
        api.getMonthlySummary(),
      ])
      setInsights(insightsData.insights || [])
      setSummary(summaryData)
    } catch (error) {
      console.error("Failed to load insights:", error)
      if (error instanceof Error && error.message.includes("401")) {
        router.push("/login")
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-background">
        <AppNavigation />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading insights...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-background">
      <AppNavigation />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-semibold mb-2">Insights</h1>
            <p className="text-muted-foreground">AI-powered recommendations to optimize your finances</p>
          </div>

          {/* Insights grid */}
          <div className="space-y-4">
            {insights.map((insight, index) => {
              const color = colorMap[insight.type] || colorMap.optimization
              const Icon = iconMap[insight.type] || CreditCard
              
              return (
                <motion.div
                  key={insight.id}
                  className="rounded-2xl border border-border bg-card p-6 hover:border-accent/50 transition-colors"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.01 }}
                >
                  <div className="flex items-start gap-4">
                    <div className={`w-12 h-12 rounded-xl ${color.bg} flex items-center justify-center shrink-0`}>
                      <Icon className={`w-6 h-6 ${color.text}`} />
                    </div>

                    <div className="flex-1">
                      <h3 className="font-semibold mb-1">{insight.title}</h3>
                      <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{insight.description}</p>

                      <div className="flex items-center gap-2">
                        {insight.impact && (
                          <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full ${color.bg} ${color.text} text-sm font-medium`}>
                            <TrendingUp className="w-3.5 h-3.5" />
                            {insight.impact}
                          </div>
                        )}
                        
                        {insight.action && (
                          <div className="text-xs text-muted-foreground">
                            {insight.action}
                          </div>
                        )}
                      </div>
                      
                      <div className="mt-2 text-xs text-muted-foreground">
                        {new Date(insight.date).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>

          {insights.length === 0 && !loading && (
            <motion.div
              className="text-center py-16"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="w-16 h-16 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No insights yet</h3>
              <p className="text-muted-foreground">Check back soon for AI-powered recommendations</p>
            </motion.div>
          )}

          {/* AI analysis section */}
          {summary && (
            <motion.div
              className="mt-8 rounded-2xl border border-accent/20 bg-accent/5 p-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold mb-2">Monthly Summary</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {summary.summary || "You're doing great! Keep optimizing your rewards and managing your finances."}
                  </p>
                  {summary.total_spend && (
                    <div className="mt-3 text-sm">
                      <span className="text-muted-foreground">Total spend: </span>
                      <span className="font-medium">${summary.total_spend.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  )
}
