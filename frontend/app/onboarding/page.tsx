"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { CheckCircle2, Circle, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

const steps = [
  { id: 1, label: "Connecting" },
  { id: 2, label: "Permissions" },
  { id: 3, label: "Linked" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [sdkLoaded, setSdkLoaded] = useState(false);

  // Check if Knot SDK is loaded
  useEffect(() => {
    const checkSDK = () => {
      if (typeof window !== "undefined" && window.KnotapiJS) {
        console.log("✅ Knot SDK (KnotapiJS) loaded successfully");
        setSdkLoaded(true);
        return true;
      }
      return false;
    };

    // Check immediately
    if (checkSDK()) return;

    // If not loaded, check every 100ms for up to 5 seconds
    let attempts = 0;
    const maxAttempts = 50;
    const interval = setInterval(() => {
      attempts++;
      if (checkSDK()) {
        clearInterval(interval);
      } else if (attempts >= maxAttempts) {
        clearInterval(interval);
        console.error("❌ Knot SDK failed to load after 5 seconds");
        setError(
          "Knot SDK not available. This may be a network issue or the SDK may not be supported in your environment."
        );
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  // Get user email on mount
  useEffect(() => {
    async function loadUser() {
      try {
        const user = await api.getCurrentUser();
        setUserEmail(user.email);
      } catch (err) {
        console.error("Failed to load user:", err);
        setError("Please log in to continue");
      }
    }
    loadUser();
  }, []);

  const handleConnect = async () => {
    if (!userEmail) {
      setError("User email not available. Please log in again.");
      return;
    }

    if (!sdkLoaded) {
      setError(
        "Knot SDK is still loading. Please wait a moment and try again."
      );
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Step 1: Get session from backend
      console.log("🎯 Starting Knot onboarding...");
      setCurrentStep(1);
      // Enable test_mode in development to avoid Knot session conflicts when testing repeatedly
      const isDevelopment = process.env.NODE_ENV === "development";
      const startResult = await api.startOnboarding(
        userEmail,
        undefined,
        isDevelopment
      );
      console.log("✅ Session created:", startResult);
      if (isDevelopment) {
        console.log(
          "🧪 Test mode enabled - using unique session ID to prevent conflicts"
        );
      }

      // Step 2: Initialize Knot SDK
      setCurrentStep(2);
      console.log("🔗 Initializing Knot SDK...");

      if (!window.KnotapiJS) {
        throw new Error("Knot SDK not available");
      }

      const KnotapiJS = window.KnotapiJS.default;
      const knotapi = new KnotapiJS();

      // Step 3: Open Knot SDK with configuration
      console.log("🎨 Opening Knot interface...");
      console.log(`🌍 Using Knot environment: ${startResult.environment}`);
      knotapi.open({
        sessionId: startResult.session_id,
        clientId: "dda0778d-9486-47f8-bd80-6f2512f9bcdb", // Your Knot client ID
        environment: startResult.environment as "development" | "production",
        product: "transaction_link",
        merchantIds: [44],
        entryPoint: "onboarding",
        useCategories: true,
        useSearch: true,

        onSuccess: async (product, details) => {
          try {
            console.log("🎯 User completed Knot linking!", product, details);
            setCurrentStep(3);

            // Tell backend the user finished linking
            const completeResult = await api.completeOnboarding(
              startResult.session_id
            );
            console.log("✅ Onboarding complete:", completeResult);
            console.log(
              `🎉 Linked ${completeResult.accounts_linked} account(s)`
            );

            // Redirect to accounts page
            setTimeout(() => {
              console.log("🚀 Redirecting to /accounts...");
              router.push("/accounts");
            }, 1000);
          } catch (err: any) {
            console.error("❌ Failed to complete onboarding:", err);
            setError(err.message || "Failed to save linked accounts.");
            setCurrentStep(0);
            setLoading(false);
          }
        },

        onError: (product, errorCode, errorDescription) => {
          console.error("❌ Knot SDK error:", errorCode, errorDescription);
          setError(`${errorCode}: ${errorDescription}`);
          setCurrentStep(0);
          setLoading(false);
        },

        onEvent: (product, event, merchant, merchantId, payload, taskId) => {
          console.log("📊 Knot event:", event, merchant, merchantId);
        },

        onExit: (product) => {
          console.log("👋 User closed Knot SDK");
          setCurrentStep(0);
          setLoading(false);
        },
      });
    } catch (err: any) {
      console.error("❌ Onboarding failed:", err);
      setError(err.message || "Failed to connect accounts. Please try again.");
      setCurrentStep(0);
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    handleConnect();
  };

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
          <p className="text-muted-foreground">
            Securely link your financial accounts through Knot
          </p>
          {!sdkLoaded && !error && (
            <p className="text-xs text-muted-foreground mt-2">
              Loading Knot SDK...
            </p>
          )}
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
                  transition={{
                    duration: 2,
                    repeat: Number.POSITIVE_INFINITY,
                    ease: "linear",
                  }}
                >
                  <Circle className="w-6 h-6 text-accent" />
                </motion.div>
              ) : (
                <Circle className="w-6 h-6 text-muted-foreground/40" />
              )}
              <span
                className={
                  currentStep >= index
                    ? "text-foreground font-medium"
                    : "text-muted-foreground"
                }
              >
                {step.label}
              </span>
            </motion.div>
          ))}
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-lg bg-destructive/10 border border-destructive/20"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-destructive">{error}</p>
                {currentStep === 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRetry}
                    className="mt-3"
                  >
                    Try Again
                  </Button>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {currentStep === 0 && (
          <Button
            onClick={handleConnect}
            className="w-full rounded-full font-medium"
            size="lg"
            disabled={loading || !userEmail || !sdkLoaded}
          >
            {loading
              ? "Connecting..."
              : !sdkLoaded
              ? "Loading Knot SDK..."
              : "Connect with Knot"}
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
  );
}
