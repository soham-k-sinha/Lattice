"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { CheckCircle2, Circle, AlertCircle, Store } from "lucide-react";
import { api } from "@/lib/api";

const steps = [
  { id: 1, label: "Connecting" },
  { id: 2, label: "Permissions" },
  { id: 3, label: "Linked" },
];

const merchants = [
  { name: "Amazon", id: 44 },
  { name: "Costco", id: 165 },
  { name: "Doordash", id: 19 },
  { name: "Instacart", id: 40 },
  { name: "Target", id: 12 },
  { name: "Ubereats", id: 36 },
  { name: "Walmart", id: 45 },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [sdkLoaded, setSdkLoaded] = useState(false);
  const [selectedMerchant, setSelectedMerchant] = useState<number | null>(null);
  const [showMerchantSelection, setShowMerchantSelection] = useState(true);

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
        // Check if token exists first
        const token = localStorage.getItem("access_token");
        if (!token) {
          console.error("❌ No access token found in localStorage");
          setError("Please log in to continue");
          setTimeout(() => router.push("/login"), 2000);
          return;
        }

        console.log("✅ Token found, fetching user info...");
        const user = await api.getCurrentUser();
        console.log("✅ User loaded:", user);
        setUserEmail(user.email);
      } catch (err) {
        console.error("❌ Failed to load user:", err);
        setError("Session expired. Please log in again.");
        localStorage.removeItem("access_token");
        setTimeout(() => router.push("/login"), 2000);
      }
    }
    loadUser();
  }, [router]);

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

    if (!selectedMerchant) {
      setError("Please select a merchant to continue.");
      return;
    }

    setLoading(true);
    setError(null);
    setShowMerchantSelection(false);

    try {
      // Step 1: Get session from backend
      console.log("🎯 Starting Knot onboarding...");
      setCurrentStep(1);
      // Enable test_mode in development to avoid Knot session conflicts when testing repeatedly
      const isDevelopment = process.env.NODE_ENV !== "production";
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
      console.log(`🏪 Using merchant ID: ${selectedMerchant}`);
      knotapi.open({
        sessionId: startResult.session_id,
        clientId: "a390e79d-2920-4440-9ba1-b747bc92790b", // Your Knot client ID
        environment: startResult.environment as "development" | "production",
        product: "transaction_link",
        merchantIds: [selectedMerchant],
        entryPoint: "onboarding",
        useCategories: true,
        useSearch: true,

        onSuccess: async (product, details) => {
          console.log("🎯🎯🎯 onSuccess callback FIRED! 🎯🎯🎯");
          console.log("🎯 Product:", product);
          console.log("🎯 Details:", JSON.stringify(details, null, 2));

          try {
            setCurrentStep(3);
            console.log("📞 About to call completeOnboarding...");
            console.log("📞 Session ID:", startResult.session_id);

            // Tell backend the user finished linking
            const completeResult = await api.completeOnboarding(
              startResult.session_id
            );
            console.log("✅✅✅ completeOnboarding response received! ✅✅✅");
            console.log(
              "✅ Response:",
              JSON.stringify(completeResult, null, 2)
            );

            // Check if backend had an error
            if (!completeResult.success) {
              throw new Error(
                completeResult.message || "Backend failed to link accounts"
              );
            }

            console.log(
              `🎉 Backend says: Linked ${completeResult.accounts_linked} account(s)`
            );

            // Warn if no accounts were linked
            if (completeResult.accounts_linked === 0) {
              console.warn("⚠️⚠️⚠️ WARNING: 0 accounts linked!");
              console.warn("⚠️ Message:", completeResult.message);
            }

            // Verify accounts were stored by fetching them
            console.log("🔍 Now fetching accounts from backend...");
            try {
              const accountsResult = await api.getAccounts();
              console.log("✅ getAccounts SUCCESS!");
              console.log(
                "✅ Response:",
                JSON.stringify(accountsResult, null, 2)
              );

              if (
                accountsResult.accounts &&
                accountsResult.accounts.length > 0
              ) {
                console.log("✅✅✅ SUCCESS: Knot integration working! ✅✅✅");
                console.log("📊 Account details:", accountsResult.accounts);
              } else {
                console.warn("⚠️⚠️⚠️ No accounts found! ⚠️⚠️⚠️");
                console.warn(
                  "This means Knot session completed but no accounts were saved"
                );
              }
            } catch (verifyErr: any) {
              console.error("❌ getAccounts failed:", verifyErr);
              console.error("❌ Error message:", verifyErr.message);
            }

            // Sync transactions for the selected merchant (and log everything)
            const merchantIdParam =
              selectedMerchant !== null ? String(selectedMerchant) : undefined;
            console.log(
              "🧾 Preparing to sync transactions for merchant:",
              merchantIdParam
            );
            try {
              const syncResult = await api.syncTransactions(
                merchantIdParam,
                100
              );
              console.log("🧾 syncTransactions SUCCESS!");
              console.log(
                "🧾 Raw sync response:",
                JSON.stringify(syncResult, null, 2)
              );
              if (syncResult.file_path) {
                console.log("🗂️ Transactions saved to:", syncResult.file_path);
              }
              if (syncResult.transactions?.length) {
                console.log(
                  `🧾 Retrieved ${syncResult.transactions.length} transaction(s)`
                );
                console.log(
                  "🧾 Sample transaction:",
                  syncResult.transactions[0]
                );
              } else {
                console.warn(
                  "⚠️ syncTransactions returned no transactions for this merchant"
                );
              }
            } catch (syncErr: any) {
              console.error("❌ syncTransactions failed:", syncErr);
              console.error("❌ Error message:", syncErr.message);
            }

            // Fetch cached transactions for additional logging
            console.log("📚 Fetching cached transactions after sync...");
            try {
              const cachedResult = await api.getTransactions(
                merchantIdParam,
                50
              );
              console.log("📚 getTransactions SUCCESS!");
              console.log(
                "📚 Cached transactions response:",
                JSON.stringify(cachedResult, null, 2)
              );
              if (cachedResult.file_path) {
                console.log(
                  "🗂️ Cached transactions file:",
                  cachedResult.file_path
                );
              }
              if (cachedResult.transactions?.length) {
                console.log(
                  `📚 Cached ${cachedResult.transactions.length} transaction(s) available`
                );
              } else {
                console.warn(
                  "⚠️ No cached transactions found even after sync. Check Knot dashboard."
                );
              }
            } catch (cachedErr: any) {
              console.error("❌ getTransactions failed:", cachedErr);
              console.error("❌ Error message:", cachedErr.message);
            }

            // Redirect to chat page
            console.log("⏳ Will redirect in 2 seconds...");
            setTimeout(() => {
              console.log("🚀 Redirecting to /chat/1...");
              router.push("/chat/1");
            }, 2000);
          } catch (err: any) {
            console.error("❌❌❌ completeOnboarding FAILED! ❌❌❌");
            console.error("❌ Error:", err);
            console.error("❌ Message:", err.message);
            console.error("❌ Stack:", err.stack);
            setError(
              err.message || "Failed to save linked accounts. Check console."
            );
            setShowMerchantSelection(true);
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
          console.log("HELLOOOOOOOOOOOO", product, event, merchant, merchantId, payload, taskId);
          console.log("📊 Knot event:", event, merchant, merchantId);
        },

        onExit: (product) => {
          console.log("👋 User closed Knot SDK without linking", product);
          setCurrentStep(0);
          setShowMerchantSelection(true);
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
    setShowMerchantSelection(true);
    setCurrentStep(0);
    setLoading(false);
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-background p-6">
      <motion.div
        className="w-full max-w-2xl"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="text-center mb-12">
          <h1 className="text-3xl font-semibold mb-3">Connect Your Accounts</h1>
          <p className="text-muted-foreground">
            {showMerchantSelection
              ? "Choose a merchant to link your account"
              : "Securely link your financial accounts through Knot"}
          </p>
          {!sdkLoaded && !error && (
            <p className="text-xs text-muted-foreground mt-2">
              Loading Knot SDK...
            </p>
          )}
        </div>

        {showMerchantSelection ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {merchants.map((merchant) => (
                <motion.button
                  key={merchant.id}
                  onClick={() => setSelectedMerchant(merchant.id)}
                  className={`p-6 rounded-lg border-2 transition-all ${
                    selectedMerchant === merchant.id
                      ? "border-accent bg-accent/10"
                      : "border-border hover:border-accent/50"
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex flex-col items-center gap-3">
                    <Store
                      className={`w-8 h-8 ${
                        selectedMerchant === merchant.id
                          ? "text-accent"
                          : "text-muted-foreground"
                      }`}
                    />
                    <span className="font-medium">{merchant.name}</span>
                  </div>
                </motion.button>
              ))}
            </div>
          </div>
        ) : (
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
        )}

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

        {showMerchantSelection && currentStep === 0 && (
          <Button
            onClick={handleConnect}
            className="w-full rounded-full font-medium mt-6"
            size="lg"
            disabled={loading || !userEmail || !sdkLoaded || !selectedMerchant}
          >
            {loading
              ? "Connecting..."
              : !sdkLoaded
              ? "Loading Knot SDK..."
              : !selectedMerchant
              ? "Select a Merchant"
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
