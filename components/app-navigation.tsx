"use client"

import { motion } from "framer-motion"
import { MessageSquare, Users, CreditCard, TrendingUp, Settings } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"

const navItems = [
  { icon: MessageSquare, href: "/chat/main", label: "Chats", key: "chat" },
  { icon: Users, href: "/groups", label: "Groups", key: "groups" },
  { icon: CreditCard, href: "/accounts", label: "Accounts", key: "accounts" },
  { icon: TrendingUp, href: "/insights", label: "Insights", key: "insights" },
]

export function AppNavigation() {
  const pathname = usePathname()

  const isActive = (key: string) => {
    if (key === "chat") return pathname?.includes("/chat")
    if (key === "groups") return pathname?.includes("/groups")
    return pathname?.includes(`/${key}`)
  }

  return (
    <motion.nav
      className="w-20 border-r border-border bg-card flex flex-col items-center py-6 gap-2"
      initial={{ x: -80, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {/* Logo */}
      <Link href="/" className="mb-8">
        <motion.div
          className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <span className="font-mono text-sm font-bold text-accent">L</span>
        </motion.div>
      </Link>

      {/* Navigation items */}
      <div className="flex-1 flex flex-col gap-2">
        {navItems.map((item) => {
          const active = isActive(item.key)
          return (
            <Link key={item.key} href={item.href}>
              <motion.div className="relative" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`w-12 h-12 rounded-xl relative ${
                    active ? "bg-accent/10 text-accent" : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                </Button>

                {/* Active indicator */}
                {active && (
                  <motion.div
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-accent rounded-r-full"
                    layoutId="nav-indicator"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
              </motion.div>
            </Link>
          )
        })}
      </div>

      {/* Settings at bottom */}
      <Link href="/settings">
        <Button
          variant="ghost"
          size="icon"
          className="w-12 h-12 rounded-xl text-muted-foreground hover:text-foreground"
        >
          <Settings className="w-5 h-5" />
        </Button>
      </Link>
    </motion.nav>
  )
}
