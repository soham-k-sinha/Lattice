"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Plus, MessageSquare, Users, X, Search, CreditCard } from "lucide-react"
import Link from "next/link"
import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { CreateGroupDialog } from "@/components/create-group-dialog"
import { api, type Chat } from "@/lib/api"

interface ChatSidebarProps {
  onClose: () => void
  currentChatId?: string
}

export function ChatSidebar({ onClose, currentChatId }: ChatSidebarProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [createGroupOpen, setCreateGroupOpen] = useState(false)
  const [chats, setChats] = useState<Chat[]>([])
  const [loading, setLoading] = useState(true)

  // Load chats from backend
  useEffect(() => {
    loadChats()
  }, [])

  const loadChats = async () => {
    try {
      setLoading(true)
      const data = await api.getChats()
      setChats(data)
    } catch (error) {
      console.error("Failed to load chats:", error)
      // Note: fetchWithAuth will automatically redirect to /login on 401
      // So we just need to fail silently here
    } finally {
      setLoading(false)
    }
  }

  const filteredChats = chats.filter((chat) => 
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

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
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
            </div>
          ) : (
            <div className="space-y-1">
              {filteredChats.map((chat) => {
                const isActive = currentChatId === chat.id.toString()
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
                            <Users className="w-4 h-4" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{chat.title}</p>
                          {chat.last_message && (
                            <p className="text-xs text-muted-foreground truncate">{chat.last_message}</p>
                          )}
                        </div>
                      </div>
                    </motion.button>
                  </Link>
                )
              })}
              {filteredChats.length === 0 && !loading && (
                <p className="text-center text-muted-foreground text-sm py-8">No chats found</p>
              )}
            </div>
          )}
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

      <CreateGroupDialog 
        open={createGroupOpen} 
        onOpenChange={setCreateGroupOpen}
        onGroupCreated={loadChats}
      />
    </>
  )
}
