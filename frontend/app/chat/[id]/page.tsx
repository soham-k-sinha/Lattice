"use client"

import { use, useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send } from "lucide-react"
import { ChatSidebar } from "@/components/chat-sidebar"
import { ContextDrawer } from "@/components/context-drawer"
import { AIMessage } from "@/components/ai-message"
import { UserMessage } from "@/components/user-message"
import { AppNavigation } from "@/components/app-navigation"
import { GroupHeader } from "@/components/group-header"
import { api, type Message as APIMessage } from "@/lib/api"

interface Message {
  id: string
  type: "user" | "ai"
  content: string
  thinking?: string[]
  action?: "card" | "split" | "tracker"
  sender?: {
    name: string
    email: string
  }
}

export default function ChatPage({ params }: { params: { id: string } }) {
  const { id } = use(params)
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [drawerType, setDrawerType] = useState<"card" | "split" | "tracker" | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [chatType, setChatType] = useState<"solo" | "group">("solo")

  // Parse chat ID (handle numeric IDs only)
  const chatId = parseInt(id)
  const isGroupChat = chatType === "group"
  const [groupMembers] = useState([
    { name: "You", email: "you@example.com" },
    { name: "Alex Chen", email: "alex@example.com" },
    { name: "Jordan Smith", email: "jordan@example.com" },
  ])

  // Load chat from backend
  useEffect(() => {
    loadChat()
  }, [id])

  const loadChat = async () => {
    // Validate chat ID
    if (isNaN(chatId)) {
      console.error("Invalid chat ID:", id)
      router.push("/chat/1") // Redirect to default chat
      return
    }

    try {
      setLoading(true)
      const chatData = await api.getChat(chatId)
      
      // Set chat type based on response
      if (chatData.type) {
        setChatType(chatData.type as "solo" | "group")
      }
      
      // Convert backend messages to component format
      const formattedMessages: Message[] = chatData.messages?.map((msg: APIMessage) => ({
        id: msg.id.toString(),
        type: msg.sender_type as "user" | "ai",
        content: msg.content,
        thinking: msg.thinking,
        action: msg.action as "card" | "split" | "tracker" | undefined,
        sender: msg.sender_type === "user" && chatData.type === "group"
          ? { name: "User", email: "user@example.com" }
          : undefined,
      })) || []
      
      setMessages(formattedMessages)
    } catch (error) {
      console.error("Failed to load chat:", error)
      // If unauthorized, redirect to login
      if (error instanceof Error && error.message.includes("401")) {
        router.push("/login")
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || sending) return

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      type: "user",
      content: input,
      sender: isGroupChat ? { name: "You", email: "you@example.com" } : undefined,
    }

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage])
    const messageContent = input
    setInput("")
    setSending(true)

    try {
      // Send message to backend
      await api.sendMessage(chatId, messageContent)
      
      // Reload chat to get AI response
      const chatData = await api.getChat(chatId)
      
      // Convert backend messages to component format
      const formattedMessages: Message[] = chatData.messages?.map((msg: APIMessage) => ({
        id: msg.id.toString(),
        type: msg.sender_type as "user" | "ai",
        content: msg.content,
        thinking: msg.thinking,
        action: msg.action as "card" | "split" | "tracker" | undefined,
        sender: msg.sender_type === "user" && isGroupChat 
          ? { name: "User", email: "user@example.com" }
          : undefined,
      })) || []
      
      setMessages(formattedMessages)
      
      // Check if AI response has an action
      const lastMessage = formattedMessages[formattedMessages.length - 1]
      if (lastMessage && lastMessage.type === "ai" && lastMessage.action) {
        setDrawerType(lastMessage.action)
        setDrawerOpen(true)
      }
    } catch (error) {
      console.error("Failed to send message:", error)
      // Remove temporary message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id))
    } finally {
      setSending(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-background items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading chat...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-background">
      <AppNavigation />

      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && <ChatSidebar onClose={() => setSidebarOpen(false)} currentChatId={id} />}
      </AnimatePresence>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {isGroupChat ? (
          <GroupHeader
            members={groupMembers}
            chatId={id}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
            sidebarOpen={sidebarOpen}
          />
        ) : (
          <header className="h-16 border-b border-border flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
              <span className="font-mono font-semibold">Lattice.</span>
            </div>
          </header>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message) => (
              <div key={message.id}>
                {message.type === "user" ? (
                  <UserMessage content={message.content} sender={message.sender} isGroupChat={isGroupChat} />
                ) : (
                  <AIMessage content={message.content} thinking={message.thinking} action={message.action} />
                )}
              </div>
            ))}
            {sending && (
              <div>
                <AIMessage 
                  content="" 
                  thinking={["Processing your request...", "Analyzing...", "Generating response..."]} 
                />
              </div>
            )}
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-border p-6">
          <div className="max-w-3xl mx-auto flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder={isGroupChat ? "Message your group..." : "Ask about cards, splits, or price tracking..."}
              className="rounded-full"
              disabled={sending}
            />
            <Button onClick={handleSend} size="icon" className="rounded-full shrink-0" disabled={sending}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Context drawer */}
      <AnimatePresence>
        {drawerOpen && drawerType && <ContextDrawer type={drawerType} onClose={() => setDrawerOpen(false)} />}
      </AnimatePresence>
    </div>
  )
}
