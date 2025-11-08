"use client"

import { motion } from "framer-motion"
import { AppNavigation } from "@/components/app-navigation"
import { Button } from "@/components/ui/button"
import { Users, Plus, DollarSign, Calendar } from "lucide-react"
import Link from "next/link"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { CreateGroupDialog } from "@/components/create-group-dialog"
import { api, type Group } from "@/lib/api"

const groupColors = [
  "from-teal-500/20 to-cyan-500/20",
  "from-violet-500/20 to-purple-500/20",
  "from-pink-500/20 to-rose-500/20",
  "from-amber-500/20 to-orange-500/20",
]

export default function GroupsPage() {
  const router = useRouter()
  const [createGroupOpen, setCreateGroupOpen] = useState(false)
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGroups()
  }, [])

  const loadGroups = async () => {
    try {
      setLoading(true)
      const data = await api.getGroups()
      setGroups(data)
    } catch (error) {
      console.error("Failed to load groups:", error)
      if (error instanceof Error && error.message.includes("401")) {
        router.push("/login")
      }
    } finally {
      setLoading(false)
    }
  }

  const formatLastActivity = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-background">
        <AppNavigation />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading groups...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-background">
      <AppNavigation />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-semibold mb-2">Groups</h1>
              <p className="text-muted-foreground">Collaborate and split costs with friends</p>
            </div>
            <Button onClick={() => setCreateGroupOpen(true)} className="rounded-full gap-2">
              <Plus className="w-4 h-4" />
              Create Group
            </Button>
          </div>

          {/* Active groups */}
          <div className="space-y-4">
            {groups.map((group, index) => (
              <motion.div
                key={group.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Link href={`/chat/${group.id}`}>
                  <motion.div
                    className="relative overflow-hidden rounded-2xl border border-border bg-card p-6 hover:border-accent/50 transition-colors"
                    whileHover={{ scale: 1.01 }}
                    transition={{ duration: 0.2 }}
                  >
                    {/* Gradient background */}
                    <div className={`absolute inset-0 bg-gradient-to-br ${groupColors[index % groupColors.length]} opacity-50`} />

                    <div className="relative">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
                            <Users className="w-6 h-6 text-accent" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">{group.name}</h3>
                            <p className="text-sm text-muted-foreground">
                              {group.members.length} members · {formatLastActivity(group.last_activity)}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex items-center gap-2 text-sm">
                          <Calendar className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground truncate">{group.context}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <DollarSign className="w-4 h-4 text-muted-foreground" />
                          <span className="font-medium">${group.total_spend.toFixed(2)} total</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </Link>
              </motion.div>
            ))}
          </div>

          {/* Empty state hint */}
          {groups.length === 0 && !loading && (
            <motion.div
              className="text-center py-16"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="w-16 h-16 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
                <Users className="w-8 h-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No groups yet</h3>
              <p className="text-muted-foreground mb-6">Create your first group to start collaborating</p>
              <Button onClick={() => setCreateGroupOpen(true)} className="rounded-full">
                Create Group
              </Button>
            </motion.div>
          )}
        </div>
      </main>

      <CreateGroupDialog 
        open={createGroupOpen} 
        onOpenChange={setCreateGroupOpen}
        onGroupCreated={loadGroups}
      />
    </div>
  )
}
