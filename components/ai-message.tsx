"use client"

import { motion, AnimatePresence } from "framer-motion"
import { useEffect, useState } from "react"

interface AIMessageProps {
  content: string
  thinking?: string[]
  action?: "card" | "split" | "tracker"
}

export function AIMessage({ content, thinking, action }: AIMessageProps) {
  const [currentThinking, setCurrentThinking] = useState(0)

  useEffect(() => {
    if (thinking && thinking.length > 0) {
      const interval = setInterval(() => {
        setCurrentThinking((prev) => {
          if (prev < thinking.length - 1) {
            return prev + 1
          }
          return prev
        })
      }, 1000)

      return () => clearInterval(interval)
    }
  }, [thinking])

  return (
    <div className="flex gap-4">
      {/* Reasoning line */}
      <div className="relative w-1 mt-1">
        {thinking ? (
          <motion.div
            className="absolute top-0 left-0 w-full bg-accent rounded-full"
            initial={{ height: "0%" }}
            animate={{ height: "100%" }}
            transition={{ duration: 2, ease: "easeInOut" }}
          />
        ) : (
          <div className="w-full h-6 bg-accent/30 rounded-full" />
        )}
      </div>

      <div className="flex-1">
        <div className="inline-block">
          <AnimatePresence mode="wait">
            {thinking ? (
              <motion.div
                key="thinking"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-card border border-border rounded-2xl px-5 py-3"
              >
                <p className="text-sm text-muted-foreground thinking-pulse">{thinking[currentThinking]}</p>
              </motion.div>
            ) : content ? (
              <motion.div
                key="content"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-card border border-border rounded-2xl px-5 py-4"
              >
                <p className="text-sm leading-relaxed">{content}</p>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
