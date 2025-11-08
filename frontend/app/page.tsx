"use client"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function LandingPage() {
  return (
    <main className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
      {/* Animated mesh background */}
      <div className="absolute inset-0 overflow-hidden opacity-30">
        <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="lattice" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
              <motion.circle
                cx="50"
                cy="50"
                r="1"
                fill="currentColor"
                className="text-accent"
                animate={{
                  r: [1, 2, 1],
                  opacity: [0.3, 0.6, 0.3],
                }}
                transition={{
                  duration: 4,
                  repeat: Number.POSITIVE_INFINITY,
                  ease: "easeInOut",
                }}
              />
              <motion.line
                x1="50"
                y1="50"
                x2="100"
                y2="50"
                stroke="currentColor"
                strokeWidth="0.5"
                className="text-muted-foreground"
                animate={{
                  opacity: [0.1, 0.3, 0.1],
                }}
                transition={{
                  duration: 3,
                  repeat: Number.POSITIVE_INFINITY,
                  ease: "easeInOut",
                }}
              />
              <motion.line
                x1="50"
                y1="50"
                x2="50"
                y2="100"
                stroke="currentColor"
                strokeWidth="0.5"
                className="text-muted-foreground"
                animate={{
                  opacity: [0.1, 0.3, 0.1],
                }}
                transition={{
                  duration: 3,
                  repeat: Number.POSITIVE_INFINITY,
                  ease: "easeInOut",
                  delay: 1.5,
                }}
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#lattice)" />
        </svg>
      </div>

      {/* Logo */}
      <motion.div
        className="absolute top-8 left-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <span className="font-mono text-xl font-semibold tracking-tight">Lattice.</span>
      </motion.div>

      {/* Main content */}
      <div className="relative z-10 max-w-3xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h1 className="text-5xl md:text-6xl font-semibold tracking-tight mb-6 text-balance">
            Think with your money.
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground mb-12 max-w-2xl mx-auto text-balance leading-relaxed">
            An AI co-pilot that plans, predicts, and pays — securely through Knot.
          </p>
        </motion.div>

        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <Button asChild size="lg" className="rounded-full px-8 font-medium">
            <Link href="/login">Get Started</Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="rounded-full px-8 font-medium bg-transparent">
            <Link href="/login">Try Demo</Link>
          </Button>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.footer
        className="absolute bottom-8 left-0 right-0 text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        <p className="text-sm text-muted-foreground">Built with Knot · Powered by MCP Agents</p>
      </motion.footer>
    </main>
  )
}
