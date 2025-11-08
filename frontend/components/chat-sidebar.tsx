"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Plus, MessageSquare, Users, X, Search } from "lucide-react"
import Link from "next/link"
import { useState } from "react"
import { Input } from "@/components/ui/input"
import { CreateGroupDialog } from "@/components/create-group-dialog"

interface ChatSidebarProps {
  onClose: () => void
  currentChatId?: string
}

const chats = [
  { id: "main", name: "Personal Finance", type: "solo", active: false },
  { id: "group1", name: "Weekend Trip", type: "group", members: 3, active: false },
  { id: "group2", name: "Dinner Plans", type: "group", members: 4, active: false },
  { id: "demo", name: "Demo Chat", type: "solo", active: false },
]

export function ChatSidebar({ onClose, currentChatId }: ChatSidebarProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [createGroupOpen, setCreateGroupOpen] = useState(false)

  const filteredChats = chats.filter((chat) => chat.name.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <>
      <motion.aside
        className="w-80 border-r border-border bg-card flex flex-col"
        initial={{ x: -320, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: -320, opacity: 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        {/* Header */}
        <div className="h-16 border-b border-border flex items-center justify-between px-4">
          <span className="font-mono font-semibold">Conversations</span>
          <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full lg:hidden">
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Search */}
        <div className="p-4 space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="pl-10 rounded-full"
            />
          </div>

          <Button
            onClick={() => setCreateGroupOpen(true)}
            className="w-full rounded-full justify-start gap-2 bg-transparent"
            variant="outline"
          >
            <Plus className="w-4 h-4" />
            Create Group
          </Button>
        </div>

        {/* Chat list */}
        <div className="flex-1 overflow-y-auto px-2">
          <div className="space-y-1">
            {filteredChats.map((chat) => {
              const isActive = currentChatId === chat.id
              return (
                <Link key={chat.id} href={`/chat/${chat.id}`}>
                  <motion.button
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      isActive ? "bg-accent/10 text-accent-foreground" : "hover:bg-muted text-muted-foreground"
                    }`}
                    whileHover={{ x: 4 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`shrink-0 ${isActive ? "text-accent" : ""}`}>
                        {chat.type === "solo" ? (
                          <MessageSquare className="w-4 h-4" />
                        ) : (
                          <div className="relative">
                            <Users className="w-4 h-4" />
                            <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-accent text-accent-foreground text-[8px] flex items-center justify-center font-medium">
                              {chat.members}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{chat.name}</p>
                        {chat.type === "group" && (
                          <p className="text-xs text-muted-foreground">{chat.members} members</p>
                        )}
                      </div>
                    </div>
                  </motion.button>
                </Link>
              )
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border space-y-2">
          <Link href="/accounts">
            <Button variant="ghost" className="w-full justify-start rounded-lg" size="sm">
              <CreditCard className="w-4 h-4 mr-2" />
              Accounts
            </Button>
          </Link>
        </div>
      </motion.aside>

      <CreateGroupDialog open={createGroupOpen} onOpenChange={setCreateGroupOpen} />
    </>
  )
}

import { CreditCard } from "lucide-react"
