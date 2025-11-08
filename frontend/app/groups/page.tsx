"use client"

import { motion } from "framer-motion"
import { AppNavigation } from "@/components/app-navigation"
import { Button } from "@/components/ui/button"
import { Users, Plus, DollarSign, MapPin } from "lucide-react"
import Link from "next/link"
import { useState } from "react"
import { CreateGroupDialog } from "@/components/create-group-dialog"

const activeGroups = [
  {
    id: "group1",
    name: "Weekend Trip",
    members: 3,
    lastActivity: "2 hours ago",
    context: "Planning an Airbnb booking",
    totalSpend: 450,
    color: "from-teal-500/20 to-cyan-500/20",
  },
  {
    id: "group2",
    name: "Dinner Plans",
    members: 4,
    lastActivity: "5 hours ago",
    context: "Restaurant reservations",
    totalSpend: 180,
    color: "from-violet-500/20 to-purple-500/20",
  },
]

export default function GroupsPage() {
  const [createGroupOpen, setCreateGroupOpen] = useState(false)

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
            {activeGroups.map((group, index) => (
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
                    <div className={`absolute inset-0 bg-gradient-to-br ${group.color} opacity-50`} />

                    <div className="relative">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
                            <Users className="w-6 h-6 text-accent" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">{group.name}</h3>
                            <p className="text-sm text-muted-foreground">
                              {group.members} members · {group.lastActivity}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex items-center gap-2 text-sm">
                          <MapPin className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground">{group.context}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <DollarSign className="w-4 h-4 text-muted-foreground" />
                          <span className="font-medium">${group.totalSpend} total</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </Link>
              </motion.div>
            ))}
          </div>

          {/* Empty state hint */}
          {activeGroups.length === 0 && (
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

      <CreateGroupDialog open={createGroupOpen} onOpenChange={setCreateGroupOpen} />
    </div>
  )
}
