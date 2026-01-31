"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Check, Zap, CreditCard, Loader2, AlertCircle } from "lucide-react";

// #region agent log
const debugLog = (location: string, message: string, data: Record<string, unknown>) => {
  fetch('http://127.0.0.1:7242/ingest/478687fd-7ff3-4069-9a5d-c1e34f5138df',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location,message,data,timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H5'})}).catch(()=>{});
};
// #endregion

const plans = [
  {
    id: "free",
    name: "Free",
    price: 0,
    period: "forever",
    features: [
      "5 applications per day",
      "Basic job matching",
      "Manual review required",
    ],
  },
  {
    id: "premium",
    name: "Premium",
    price: 29,
    period: "month",
    features: [
      "20 applications per day",
      "AI-powered cover letters",
      "3 concurrent operations",
      "Priority support",
    ],
    popular: true,
  },
  {
    id: "elite",
    name: "Elite",
    price: 39,
    period: "month",
    features: [
      "50 applications per day",
      "AI-powered cover letters",
      "5 concurrent operations",
      "Priority support",
      "Resume optimization",
      "Interview preparation",
    ],
  },
];

export default function BillingPage() {
  const { data: usage, isLoading, error } = useQuery({
    queryKey: ["usage"],
    queryFn: async () => {
      // #region agent log
      debugLog('billing/page.tsx:fetch', 'Fetching usage data', {});
      // #endregion
      const result = await api.getUsage();
      // #region agent log
      debugLog('billing/page.tsx:fetchSuccess', 'Usage data fetched', { plan: result.plan, used: result.used_today });
      // #endregion
      return result;
    },
  });

  // #region agent log
  if (error) {
    debugLog('billing/page.tsx:error', 'Usage fetch error', { error: error instanceof Error ? error.message : 'Unknown' });
  }
  // #endregion

  const handleUpgrade = async (planId: string) => {
    // In production, this would redirect to Stripe checkout
    alert(`Upgrading to ${planId} plan - Stripe checkout would open here`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <AlertCircle className="w-12 h-12 text-error-500" />
        <p className="text-error-500">Failed to load billing data</p>
        <p className="text-neutral-400 text-sm">{error instanceof Error ? error.message : "Unknown error"}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold">Billing & Plans</h1>
        <p className="text-neutral-400">
          Manage your subscription and view usage
        </p>
      </div>

      {/* Current Usage */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Current Usage</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-neutral-400 text-sm">Current Plan</p>
            <p className="text-2xl font-bold capitalize">{usage?.plan || "Free"}</p>
          </div>
          <div>
            <p className="text-neutral-400 text-sm">Applications Today</p>
            <p className="text-2xl font-bold">
              {usage?.used_today || 0} / {usage?.daily_limit || 5}
            </p>
          </div>
          <div>
            <p className="text-neutral-400 text-sm">Remaining</p>
            <p className="text-2xl font-bold text-success-500">
              {usage?.remaining_today || 5}
            </p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-6">
          <div className="h-2 bg-neutral-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 rounded-full transition-all"
              style={{
                width: `${((usage?.used_today || 0) / (usage?.daily_limit || 5)) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Plans */}
      <div>
        <h2 className="text-lg font-semibold mb-6">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`glass-card p-6 relative ${
                plan.popular ? "border-primary-500" : ""
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-primary-500 text-xs font-semibold rounded-full">
                  Most Popular
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold mb-2">{plan.name}</h3>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  {plan.period !== "forever" && (
                    <span className="text-neutral-400">/{plan.period}</span>
                  )}
                </div>
              </div>

              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-success-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-neutral-300">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleUpgrade(plan.id)}
                disabled={usage?.plan === plan.id}
                className={`w-full py-3 rounded-xl font-semibold transition-colors flex items-center justify-center gap-2 ${
                  usage?.plan === plan.id
                    ? "bg-neutral-700 text-neutral-400 cursor-not-allowed"
                    : plan.popular
                    ? "bg-primary-600 hover:bg-primary-500"
                    : "bg-neutral-800 hover:bg-neutral-700"
                }`}
              >
                {usage?.plan === plan.id ? (
                  "Current Plan"
                ) : plan.id === "free" ? (
                  "Downgrade"
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    Upgrade
                  </>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Payment Method */}
      {usage?.plan !== "free" && (
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-neutral-800 rounded-xl flex items-center justify-center">
                <CreditCard className="w-6 h-6" />
              </div>
              <div>
                <p className="font-medium">Manage Billing</p>
                <p className="text-sm text-neutral-400">
                  Update payment method or cancel subscription
                </p>
              </div>
            </div>
            <button className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-xl transition-colors">
              Open Portal
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
