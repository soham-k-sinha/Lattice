"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { X, CreditCard, Receipt, TrendingUp } from "lucide-react"

interface ContextDrawerProps {
  type: "card" | "split" | "tracker"
  onClose: () => void
}

export function ContextDrawer({ type, onClose }: ContextDrawerProps) {
  return (
    <motion.div
      className="w-96 border-l border-border bg-card flex flex-col"
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      {/* Header */}
      <div className="h-16 border-b border-border flex items-center justify-between px-6">
        <div className="flex items-center gap-2">
          {type === "card" && <CreditCard className="w-4 h-4" />}
          {type === "split" && <Receipt className="w-4 h-4" />}
          {type === "tracker" && <TrendingUp className="w-4 h-4" />}
          <span className="font-medium">
            {type === "card" && "Card Optimizer"}
            {type === "split" && "Smart Split"}
            {type === "tracker" && "Price Tracker"}
          </span>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full">
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {type === "card" && <CardOptimizerContent />}
        {type === "split" && <SmartSplitContent />}
        {type === "tracker" && <PriceTrackerContent />}
      </div>
    </motion.div>
  )
}

function CardOptimizerContent() {
  return (
    <div className="space-y-6">
      <div className="bg-accent/10 rounded-xl p-5 border border-accent/20">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-12 h-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded"></div>
          <div>
            <p className="font-semibold">Discover It</p>
            <p className="text-xs text-muted-foreground">****1234</p>
          </div>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Cashback</span>
            <span className="font-medium">$12.50 (5%)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Utilization</span>
            <span className="font-medium">23%</span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <h4 className="text-sm font-medium">Why this card?</h4>
        <div className="space-y-2">
          <div className="flex gap-2 text-sm">
            <div className="w-1 h-1 rounded-full bg-accent mt-2"></div>
            <p className="text-muted-foreground">5% Amazon category this month</p>
          </div>
          <div className="flex gap-2 text-sm">
            <div className="w-1 h-1 rounded-full bg-accent mt-2"></div>
            <p className="text-muted-foreground">Low utilization helps credit score</p>
          </div>
        </div>
      </div>

      <Button className="w-full rounded-full">Use this card</Button>
    </div>
  )
}

function SmartSplitContent() {
  const splits = [
    { name: "You", amount: 47.5, status: "paid" },
    { name: "Sarah", amount: 32.0, status: "pending" },
    { name: "Mike", amount: 28.5, status: "pending" },
  ]

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        {splits.map((split) => (
          <div key={split.name} className="flex items-center justify-between p-4 bg-muted/50 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent to-reasoning flex items-center justify-center text-sm font-semibold text-white">
                {split.name[0]}
              </div>
              <span className="font-medium">{split.name}</span>
            </div>
            <div className="text-right">
              <p className="font-semibold">${split.amount.toFixed(2)}</p>
              <p className="text-xs text-muted-foreground">{split.status === "paid" ? "✓ Paid" : "⏳ Pending"}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="pt-4 border-t border-border">
        <div className="flex justify-between mb-4">
          <span className="text-sm text-muted-foreground">Total</span>
          <span className="font-semibold">$108.00</span>
        </div>
        <Button className="w-full rounded-full">Settle now</Button>
      </div>
    </div>
  )
}

function PriceTrackerContent() {
  return (
    <div className="space-y-6">
      <div className="bg-muted/30 rounded-xl p-5">
        <p className="text-sm text-muted-foreground mb-2">Current Price</p>
        <p className="text-3xl font-semibold mb-4">$459</p>
        <div className="h-32 flex items-end gap-1">
          {[65, 70, 68, 72, 69, 75, 71, 68, 72, 70].map((height, i) => (
            <div key={i} className="flex-1 bg-accent/30 rounded-t" style={{ height: `${height}%` }}></div>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Predicted drop</span>
          <span className="font-medium">23% in 2 weeks</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Best time to buy</span>
          <span className="font-medium">Dec 15-20</span>
        </div>
      </div>

      <Button className="w-full rounded-full">Set alert</Button>
    </div>
  )
}
