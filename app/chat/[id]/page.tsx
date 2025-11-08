"use client"

import { use, useState } from "react"
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
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [drawerType, setDrawerType] = useState<"card" | "split" | "tracker" | null>(null)

  const isGroupChat = id.startsWith("group")
  const [groupMembers] = useState([
    { name: "You", email: "you@example.com" },
    { name: "Alex Chen", email: "alex@example.com" },
    { name: "Jordan Smith", email: "jordan@example.com" },
  ])

  const [messages, setMessages] = useState<Message[]>(
    isGroupChat
      ? [
          {
            id: "1",
            type: "ai",
            content: "I'm analyzing your group conversation. I'll help you plan, split costs, and optimize payments.",
          },
          {
            id: "2",
            type: "user",
            content: "Hey everyone! Should we book that Airbnb for the weekend trip?",
            sender: { name: "Alex Chen", email: "alex@example.com" },
          },
          {
            id: "3",
            type: "user",
            content: "Yeah I'm in! It's $450 total right?",
            sender: { name: "Jordan Smith", email: "jordan@example.com" },
          },
        ]
      : [
          {
            id: "1",
            type: "ai",
            content:
              "Hi! I'm Lattice, your financial AI co-pilot. Ask me about card recommendations, splitting bills, or tracking prices.",
          },
        ],
  )
  const [input, setInput] = useState("")

  const simulateAIResponse = (userInput: string) => {
    // Simulate thinking stages
    const thinkingId = `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`

    const thinkingStages = isGroupChat
      ? ["Understanding group context...", "Analyzing conversation...", "Calculating optimal splits..."]
      : ["Checking your cards...", "Comparing rewards and balances..."]

    setMessages((prev) => [
      ...prev,
      {
        id: thinkingId,
        type: "ai",
        content: "",
        thinking: thinkingStages,
      },
    ])

    // After 2 seconds, show final response
    setTimeout(() => {
      let response = {
        content: "I can help you with that! Try asking about card recommendations or splitting receipts.",
        action: undefined as "card" | "split" | "tracker" | undefined,
      }

      if (isGroupChat) {
        if (userInput.toLowerCase().includes("airbnb") || userInput.toLowerCase().includes("book")) {
          response = {
            content:
              "I see you're planning an Airbnb. Split $450 three ways = $150 each. Alex should use Chase Sapphire for 3x points on travel.",
            action: "split" as const,
          }
        } else if (userInput.toLowerCase().includes("dinner") || userInput.toLowerCase().includes("restaurant")) {
          response = {
            content: "For dining, I recommend splitting evenly. The person paying should use Amex Gold for 4x points.",
            action: "split" as const,
          }
        }
      } else {
        if (userInput.toLowerCase().includes("card")) {
          response = {
            content: "Use Discover — you'll earn $12 cashback.",
            action: "card" as const,
          }
        } else if (userInput.toLowerCase().includes("split")) {
          response = {
            content: "I've parsed the receipt. Here's the suggested split.",
            action: "split" as const,
          }
        }
      }

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === thinkingId
            ? {
                ...msg,
                content: response.content,
                thinking: undefined,
                action: response.action,
              }
            : msg,
        ),
      )

      if (response.action) {
        setDrawerType(response.action)
        setDrawerOpen(true)
      }
    }, 2000)
  }

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      type: "user",
      content: input,
      sender: isGroupChat ? { name: "You", email: "you@example.com" } : undefined,
    }

    setMessages((prev) => [...prev, userMessage])
    simulateAIResponse(input)
    setInput("")
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
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-border p-6">
          <div className="max-w-3xl mx-auto flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder={isGroupChat ? "Message your group..." : "Ask about cards, splits, or price tracking..."}
              className="rounded-full"
            />
            <Button onClick={handleSend} size="icon" className="rounded-full shrink-0">
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
