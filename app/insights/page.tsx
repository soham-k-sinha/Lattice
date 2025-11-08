"use client"

import { motion } from "framer-motion"
import { AppNavigation } from "@/components/app-navigation"
import { TrendingUp, TrendingDown, CreditCard, Users, Sparkles } from "lucide-react"

const insights = [
  {
    id: 1,
    type: "optimization",
    title: "Switch cards for dining",
    description: "Use Amex Gold instead of Chase Sapphire at restaurants to earn 4x points instead of 3x",
    potential: "+$47/month",
    color: "teal",
  },
  {
    id: 2,
    type: "spending",
    title: "Group spending up 23%",
    description: "Weekend Trip group has higher spending this month. Consider budget limits.",
    trend: "up",
    color: "violet",
  },
  {
    id: 3,
    type: "rewards",
    title: "Maximize Q4 categories",
    description: "Discover 5% cashback on PayPal expires in 2 weeks. You've earned $78 so far.",
    potential: "+$22 available",
    color: "blue",
  },
]

export default function InsightsPage() {
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
            {insights.map((insight, index) => (
              <motion.div
                key={insight.id}
                className="rounded-2xl border border-border bg-card p-6 hover:border-accent/50 transition-colors"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.01 }}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`w-12 h-12 rounded-xl ${
                      insight.color === "teal"
                        ? "bg-teal-500/10"
                        : insight.color === "violet"
                          ? "bg-violet-500/10"
                          : "bg-blue-500/10"
                    } flex items-center justify-center shrink-0`}
                  >
                    {insight.type === "optimization" && (
                      <CreditCard className={`w-6 h-6 ${insight.color === "teal" ? "text-teal-500" : "text-accent"}`} />
                    )}
                    {insight.type === "spending" && <Users className="w-6 h-6 text-violet-500" />}
                    {insight.type === "rewards" && <Sparkles className="w-6 h-6 text-blue-500" />}
                  </div>

                  <div className="flex-1">
                    <h3 className="font-semibold mb-1">{insight.title}</h3>
                    <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{insight.description}</p>

                    {insight.potential && (
                      <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent/10 text-accent text-sm font-medium">
                        <TrendingUp className="w-3.5 h-3.5" />
                        {insight.potential}
                      </div>
                    )}

                    {insight.trend && (
                      <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-violet-500/10 text-violet-500 text-sm font-medium">
                        {insight.trend === "up" ? (
                          <TrendingUp className="w-3.5 h-3.5" />
                        ) : (
                          <TrendingDown className="w-3.5 h-3.5" />
                        )}
                        Trending {insight.trend}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* AI analysis section */}
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
                  You've optimized <span className="text-foreground font-medium">$127</span> in rewards this month. Your
                  group spending is up but well within budget. Keep using your Amex Gold for dining to maximize points.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
