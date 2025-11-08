import type React from "react"
import type { Metadata } from "next"
import { Geist } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import Script from "next/script"
import "./globals.css"

const geist = Geist({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Lattice - Think with your money",
  description: "An AI co-pilot that plans, predicts, and pays",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        {/* Knot SDK - Official CDN */}
        <Script
          src="https://unpkg.com/knotapi-js@next"
          strategy="beforeInteractive"
        />
      </head>
      <body className={`${geist.className} antialiased`} suppressHydrationWarning>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
