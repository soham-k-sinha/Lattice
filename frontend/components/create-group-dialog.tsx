"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { X, Mail, Check, Sparkles } from "lucide-react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"

interface CreateGroupDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onGroupCreated?: () => void
}

export function CreateGroupDialog({ open, onOpenChange, onGroupCreated }: CreateGroupDialogProps) {
  const router = useRouter()
  const [groupName, setGroupName] = useState("")
  const [emailInput, setEmailInput] = useState("")
  const [members, setMembers] = useState<string[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState("")

  const validateEmail = (email: string) => {
    return email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)
  }

  const addMember = () => {
    if (emailInput && validateEmail(emailInput) && !members.includes(emailInput)) {
      setMembers([...members, emailInput])
      setEmailInput("")
    }
  }

  const removeMember = (email: string) => {
    setMembers(members.filter((m) => m !== email))
  }

  const createGroup = async () => {
    if (!groupName || members.length === 0) return

    setIsCreating(true)
    setError("")

    try {
      // Call backend API to create group
      const newGroup = await api.createGroup(groupName, members)
      
      // Close dialog
      onOpenChange(false)

      // Reset form
      setGroupName("")
      setMembers([])
      
      // Notify parent to reload chats list (to show new group in sidebar)
      if (onGroupCreated) {
        onGroupCreated()
      }
      
      // Navigate to the new group chat
      router.push(`/chat/${newGroup.id}`)
    } catch (err: any) {
      setError(err.message || "Failed to create group")
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">Create Group</DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Error message */}
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
              {error}
            </div>
          )}
          
          {/* Group name */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Group Name</label>
            <Input
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              placeholder="Weekend Trip, Dinner Plans..."
              className="rounded-lg"
            />
          </div>

          {/* Add members */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Add Members</label>
            <div className="flex gap-2">
              <Input
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addMember()}
                placeholder="email@example.com"
                className="rounded-lg flex-1"
                type="email"
              />
              <Button
                onClick={addMember}
                size="icon"
                className="rounded-lg shrink-0"
                disabled={!emailInput || !validateEmail(emailInput)}
              >
                <Mail className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Members list */}
          <AnimatePresence>
            {members.length > 0 && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="space-y-2"
              >
                <label className="text-sm font-medium text-muted-foreground">
                  {members.length} {members.length === 1 ? "Member" : "Members"}
                </label>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {members.map((email, index) => (
                    <motion.div
                      key={email}
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      exit={{ x: 20, opacity: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-accent/20 text-accent flex items-center justify-center">
                          <Check className="w-3 h-3" />
                        </div>
                        <span className="text-sm">{email}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeMember(email)}
                        className="h-6 w-6 rounded-full"
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* AI insight */}
          {members.length > 0 && groupName && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 rounded-lg bg-accent/5 border border-accent/20"
            >
              <div className="flex gap-2">
                <Sparkles className="w-4 h-4 text-accent shrink-0 mt-0.5" />
                <p className="text-sm text-muted-foreground">
                  I'll analyze your group conversations to help with planning, splitting costs, and optimizing payments.
                </p>
              </div>
            </motion.div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="flex-1 rounded-lg"
            disabled={isCreating}
          >
            Cancel
          </Button>
          <Button
            onClick={createGroup}
            className="flex-1 rounded-lg"
            disabled={!groupName || members.length === 0 || isCreating}
          >
            {isCreating ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
              >
                <Sparkles className="w-4 h-4" />
              </motion.div>
            ) : (
              "Create Group"
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
