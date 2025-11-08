"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { CheckCircle2, Circle } from "lucide-react"

const steps = [
  { id: 1, label: "Connecting" },
  { id: 2, label: "Permissions" },
  { id: 3, label: "Linked" },
]

export default function OnboardingPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)

  const handleConnect = () => {
    setCurrentStep(1)
    setTimeout(() => setCurrentStep(2), 1500)
    setTimeout(() => setCurrentStep(3), 3000)
    setTimeout(() => router.push("/chat/main"), 4000)
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-background p-6">
      <motion.div
        className="w-full max-w-md"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="text-center mb-12">
          <h1 className="text-3xl font-semibold mb-3">Connect Your Accounts</h1>
          <p className="text-muted-foreground">Securely link your financial accounts through Knot</p>
        </div>

        <div className="space-y-6 mb-12">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              className="flex items-center gap-4"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              {currentStep > index ? (
                <CheckCircle2 className="w-6 h-6 text-accent" />
              ) : currentStep === index ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                >
                  <Circle className="w-6 h-6 text-accent" />
                </motion.div>
              ) : (
                <Circle className="w-6 h-6 text-muted-foreground/40" />
              )}
              <span className={currentStep >= index ? "text-foreground font-medium" : "text-muted-foreground"}>
                {step.label}
              </span>
            </motion.div>
          ))}
        </div>

        {currentStep === 0 && (
          <Button onClick={handleConnect} className="w-full rounded-full font-medium" size="lg">
            Connect with Knot
          </Button>
        )}

        {currentStep > 0 && currentStep < 3 && (
          <div className="text-center">
            <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
              <motion.div
                className="w-2 h-2 rounded-full bg-accent"
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY }}
              />
              Establishing secure connection...
            </div>
          </div>
        )}
      </motion.div>
    </main>
  )
}
