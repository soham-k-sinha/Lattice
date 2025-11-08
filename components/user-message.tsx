"use client"

import { motion } from "framer-motion"

interface UserMessageProps {
  content: string
  sender?: {
    name: string
    email: string
  }
  isGroupChat?: boolean
}

export function UserMessage({ content, sender, isGroupChat }: UserMessageProps) {
  const isCurrentUser = sender?.name === "You"

  return (
    <motion.div
      className={`flex ${isCurrentUser ? "justify-end" : "justify-start"}`}
      initial={{ opacity: 0, x: isCurrentUser ? 20 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="max-w-[80%]">
        {isGroupChat && !isCurrentUser && sender && (
          <motion.p
            className="text-xs text-muted-foreground mb-1.5 ml-3 font-medium"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            {sender.name}
          </motion.p>
        )}

        <div
          className={`rounded-2xl px-5 py-3 ${
            isCurrentUser ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
          }`}
        >
          <p className="text-sm leading-relaxed">{content}</p>
        </div>
      </div>
    </motion.div>
  )
}
