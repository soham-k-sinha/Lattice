"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Menu, MoreVertical, UserPlus } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

interface GroupHeaderProps {
  members: Array<{ name: string; email: string }>
  chatId: string
  onToggleSidebar: () => void
  sidebarOpen: boolean
}

export function GroupHeader({ members, chatId, onToggleSidebar, sidebarOpen }: GroupHeaderProps) {
  const groupName = chatId === "group1" ? "Weekend Trip" : "Group Chat"

  return (
    <header className="h-16 border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        {!sidebarOpen && (
          <Button variant="ghost" size="icon" onClick={onToggleSidebar} className="rounded-full">
            <Menu className="w-5 h-5" />
          </Button>
        )}

        {/* Group avatar stack */}
        <div className="flex items-center gap-3">
          <motion.div className="relative flex items-center" whileHover={{ scale: 1.05 }}>
            {members.slice(0, 3).map((member, index) => (
              <div
                key={member.email}
                className="w-8 h-8 rounded-full bg-accent/20 border-2 border-background flex items-center justify-center text-xs font-medium text-accent"
                style={{ marginLeft: index > 0 ? "-8px" : "0", zIndex: members.length - index }}
              >
                {member.name.charAt(0)}
              </div>
            ))}
          </motion.div>

          <div>
            <h2 className="font-semibold text-sm">{groupName}</h2>
            <p className="text-xs text-muted-foreground">{members.length} members</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="rounded-full">
          <UserPlus className="w-4 h-4" />
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="rounded-full">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>View Members</DropdownMenuItem>
            <DropdownMenuItem>Group Settings</DropdownMenuItem>
            <DropdownMenuItem className="text-destructive">Leave Group</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
