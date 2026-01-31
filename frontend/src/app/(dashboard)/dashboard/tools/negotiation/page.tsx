"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  DollarSign,
  Loader2,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
  CheckCircle,
  Copy,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from "lucide-react";
import {
  api,
  OfferDetails,
  NegotiationAnalyzeResponse,
  NegotiationStrategyResponse,
} from "@/lib/api";

type Phase = "input" | "analysis" | "strategy";

export default function NegotiationPage() {
  const [phase, setPhase] = useState<Phase>("input");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [targetRole, setTargetRole] = useState("");
  const [location, setLocation] = useState("");
  const [yearsExperience, setYearsExperience] = useState(5);
  const [competingOffers, setCompetingOffers] = useState(0);
  const [currentSalary, setCurrentSalary] = useState<number | "">("");

  // Offer details
  const [baseSalary, setBaseSalary] = useState<number | "">("");
  const [currency, setCurrency] = useState("USD");
  const [signingBonus, setSigningBonus] = useState<number | "">("");
  const [annualBonus, setAnnualBonus] = useState<number | "">("");
  const [equityValue, setEquityValue] = useState<number | "">("");
  const [equityYears, setEquityYears] = useState(4);
  const [ptoDays, setPtoDays] = useState<number | "">("");
  const [remotePolicy, setRemotePolicy] = useState<"remote" | "hybrid" | "onsite" | "">("");

  // Results
  const [analysis, setAnalysis] = useState<NegotiationAnalyzeResponse | null>(null);
  const [strategy, setStrategy] = useState<NegotiationStrategyResponse | null>(null);

  // Strategy form
  const [targetSalary, setTargetSalary] = useState<number | "">("");
  const [riskTolerance, setRiskTolerance] = useState<"low" | "medium" | "high">("medium");

  // UI state
  const [expandedScript, setExpandedScript] = useState<string | null>(null);
  const [copiedScript, setCopiedScript] = useState<string | null>(null);

  const buildOfferDetails = (): OfferDetails => ({
    base_salary: Number(baseSalary) || 0,
    currency,
    signing_bonus: signingBonus ? Number(signingBonus) : null,
    annual_bonus_percent: annualBonus ? Number(annualBonus) : null,
    equity_value: equityValue ? Number(equityValue) : null,
    equity_vesting_years: equityValue ? equityYears : null,
    pto_days: ptoDays ? Number(ptoDays) : null,
    remote_policy: remotePolicy || null,
  });

  const analyzeOffer = async () => {
    if (!baseSalary || !targetRole || !location) {
      setError("Please fill in required fields");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.analyzeOffer({
        offer: buildOfferDetails(),
        target_role: targetRole,
        location,
        years_experience: yearsExperience,
        competing_offers: competingOffers,
        current_salary: currentSalary ? Number(currentSalary) : undefined,
      });

      setAnalysis(response);
      setPhase("analysis");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze offer");
    } finally {
      setIsLoading(false);
    }
  };

  const getStrategy = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.getNegotiationStrategy({
        offer: buildOfferDetails(),
        target_role: targetRole,
        location,
        years_experience: yearsExperience,
        target_salary: targetSalary ? Number(targetSalary) : undefined,
        risk_tolerance: riskTolerance,
      });

      setStrategy(response);
      setPhase("strategy");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate strategy");
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, scriptId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedScript(scriptId);
    setTimeout(() => setCopiedScript(null), 2000);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getPositionIcon = (position: string) => {
    switch (position) {
      case "above_market":
        return <TrendingUp className="w-5 h-5 text-emerald-400" />;
      case "below_market":
        return <TrendingDown className="w-5 h-5 text-red-400" />;
      default:
        return <Minus className="w-5 h-5 text-amber-400" />;
    }
  };

  const getPositionColor = (position: string) => {
    switch (position) {
      case "above_market":
        return "text-emerald-400";
      case "below_market":
        return "text-red-400";
      default:
        return "text-amber-400";
    }
  };

  // Input Phase
  if (phase === "input") {
    return (
      <div className="max-w-3xl mx-auto">
        <Link
          href="/dashboard/tools"
          className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Tools
        </Link>

        <div className="glass-card p-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h1 className="text-2xl font-display font-bold">Offer Negotiation Advisor</h1>
              <p className="text-neutral-400">Analyze your offer and get strategic advice</p>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-6">
            {/* Job Info */}
            <div>
              <h3 className="text-sm font-medium text-neutral-300 mb-3">Job Information</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Target Role *</label>
                  <input
                    type="text"
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    placeholder="e.g., Senior Software Engineer"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Location *</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g., San Francisco, CA"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Years of Experience</label>
                  <input
                    type="number"
                    value={yearsExperience}
                    onChange={(e) => setYearsExperience(Number(e.target.value))}
                    min={0}
                    max={50}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Competing Offers</label>
                  <input
                    type="number"
                    value={competingOffers}
                    onChange={(e) => setCompetingOffers(Number(e.target.value))}
                    min={0}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>

            {/* Offer Details */}
            <div>
              <h3 className="text-sm font-medium text-neutral-300 mb-3">Offer Details</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm text-neutral-400 mb-1">Base Salary *</label>
                  <div className="flex gap-2">
                    <select
                      value={currency}
                      onChange={(e) => setCurrency(e.target.value)}
                      className="px-3 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="GBP">GBP</option>
                      <option value="CAD">CAD</option>
                    </select>
                    <input
                      type="number"
                      value={baseSalary}
                      onChange={(e) => setBaseSalary(e.target.value ? Number(e.target.value) : "")}
                      placeholder="150000"
                      className="flex-1 px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Signing Bonus</label>
                  <input
                    type="number"
                    value={signingBonus}
                    onChange={(e) => setSigningBonus(e.target.value ? Number(e.target.value) : "")}
                    placeholder="25000"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Annual Bonus %</label>
                  <input
                    type="number"
                    value={annualBonus}
                    onChange={(e) => setAnnualBonus(e.target.value ? Number(e.target.value) : "")}
                    placeholder="15"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Equity Value</label>
                  <input
                    type="number"
                    value={equityValue}
                    onChange={(e) => setEquityValue(e.target.value ? Number(e.target.value) : "")}
                    placeholder="100000"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Vesting Years</label>
                  <input
                    type="number"
                    value={equityYears}
                    onChange={(e) => setEquityYears(Number(e.target.value))}
                    min={1}
                    max={10}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">PTO Days</label>
                  <input
                    type="number"
                    value={ptoDays}
                    onChange={(e) => setPtoDays(e.target.value ? Number(e.target.value) : "")}
                    placeholder="20"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Remote Policy</label>
                  <select
                    value={remotePolicy}
                    onChange={(e) => setRemotePolicy(e.target.value as typeof remotePolicy)}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Not specified</option>
                    <option value="remote">Remote</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="onsite">On-site</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Current Salary</label>
                  <input
                    type="number"
                    value={currentSalary}
                    onChange={(e) => setCurrentSalary(e.target.value ? Number(e.target.value) : "")}
                    placeholder="Optional"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={analyzeOffer}
              disabled={isLoading || !baseSalary || !targetRole || !location}
              className="w-full py-4 bg-amber-600 hover:bg-amber-500 disabled:bg-amber-600/50 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Analyze Offer
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Analysis Phase
  if (phase === "analysis" && analysis) {
    return (
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => setPhase("input")}
          className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Edit
        </button>

        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid md:grid-cols-3 gap-4">
            <div className="glass-card p-5 text-center">
              <div className="text-sm text-neutral-400 mb-1">Total Compensation</div>
              <div className="text-2xl font-bold text-primary-400">
                {formatCurrency(analysis.total_compensation)}
              </div>
              <div className="text-xs text-neutral-500">Annual value</div>
            </div>
            <div className="glass-card p-5 text-center">
              <div className="text-sm text-neutral-400 mb-1">Market Position</div>
              <div className={`text-2xl font-bold flex items-center justify-center gap-2 ${getPositionColor(analysis.market_comparison.position)}`}>
                {getPositionIcon(analysis.market_comparison.position)}
                {analysis.market_comparison.position.replace("_", " ")}
              </div>
              <div className="text-xs text-neutral-500">
                {analysis.market_comparison.percentile}th percentile
              </div>
            </div>
            <div className="glass-card p-5 text-center">
              <div className="text-sm text-neutral-400 mb-1">Negotiation Room</div>
              <div className={`text-2xl font-bold ${
                analysis.negotiation_room === "high"
                  ? "text-emerald-400"
                  : analysis.negotiation_room === "low"
                  ? "text-red-400"
                  : "text-amber-400"
              }`}>
                {analysis.negotiation_room.toUpperCase()}
              </div>
              <div className="text-xs text-neutral-500">Potential for increase</div>
            </div>
          </div>

          {/* Market Comparison */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Market Comparison</h3>
            <div className="relative h-8 bg-neutral-800 rounded-full mb-4">
              <div
                className="absolute top-0 left-0 h-full bg-gradient-to-r from-red-500/50 via-amber-500/50 to-emerald-500/50 rounded-full"
                style={{ width: "100%" }}
              />
              <div
                className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg border-2 border-primary-500"
                style={{
                  left: `${Math.min(Math.max(analysis.market_comparison.percentile, 5), 95)}%`,
                  transform: "translate(-50%, -50%)",
                }}
              />
            </div>
            <div className="flex justify-between text-sm">
              <div>
                <div className="text-neutral-400">Low</div>
                <div className="font-medium">{formatCurrency(analysis.market_comparison.market_low)}</div>
              </div>
              <div className="text-center">
                <div className="text-neutral-400">Median</div>
                <div className="font-medium">{formatCurrency(analysis.market_comparison.market_median)}</div>
              </div>
              <div className="text-right">
                <div className="text-neutral-400">High</div>
                <div className="font-medium">{formatCurrency(analysis.market_comparison.market_high)}</div>
              </div>
            </div>
          </div>

          {/* Strengths & Concerns */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-400" />
                Offer Strengths
              </h3>
              <ul className="space-y-2">
                {analysis.strengths.map((s, idx) => (
                  <li key={idx} className="text-sm text-neutral-300 flex items-start gap-2">
                    <span className="text-emerald-400 mt-0.5">•</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-amber-400" />
                Potential Concerns
              </h3>
              <ul className="space-y-2">
                {analysis.concerns.map((c, idx) => (
                  <li key={idx} className="text-sm text-neutral-300 flex items-start gap-2">
                    <span className="text-amber-400 mt-0.5">•</span>
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Priority Items */}
          {analysis.priority_items.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4">Priority Negotiation Items</h3>
              <div className="flex flex-wrap gap-2">
                {analysis.priority_items.map((item, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 bg-primary-500/20 text-primary-400 rounded-full text-sm"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Get Strategy */}
          <div className="glass-card p-6 bg-gradient-to-br from-amber-950/30 to-transparent">
            <h3 className="text-lg font-semibold mb-4">Generate Negotiation Strategy</h3>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-neutral-400 mb-1">Target Salary (Optional)</label>
                <input
                  type="number"
                  value={targetSalary}
                  onChange={(e) => setTargetSalary(e.target.value ? Number(e.target.value) : "")}
                  placeholder={`e.g., ${Math.round(analysis.market_comparison.market_high)}`}
                  className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm text-neutral-400 mb-1">Risk Tolerance</label>
                <select
                  value={riskTolerance}
                  onChange={(e) => setRiskTolerance(e.target.value as typeof riskTolerance)}
                  className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="low">Low - Conservative approach</option>
                  <option value="medium">Medium - Balanced approach</option>
                  <option value="high">High - Aggressive approach</option>
                </select>
              </div>
            </div>
            <button
              onClick={getStrategy}
              disabled={isLoading}
              className="w-full py-3 bg-amber-600 hover:bg-amber-500 disabled:bg-amber-600/50 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating Strategy...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Get Negotiation Strategy
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Strategy Phase
  if (phase === "strategy" && strategy) {
    const scripts = [
      { id: "initial", title: "Initial Response", content: strategy.scripts.initial_response },
      { id: "email", title: "Counter-Offer Email", content: strategy.scripts.counter_offer_email },
      { id: "phone", title: "Phone Script", content: strategy.scripts.phone_script },
    ];

    return (
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => setPhase("analysis")}
          className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Analysis
        </button>

        <div className="space-y-6">
          {/* Recommended Counter */}
          <div className="glass-card p-6 text-center bg-gradient-to-br from-emerald-950/30 to-transparent">
            <div className="text-sm text-neutral-400 mb-2">Recommended Counter-Offer</div>
            <div className="text-4xl font-bold text-emerald-400 mb-2">
              {formatCurrency(strategy.recommended_counter)}
            </div>
            <div className="text-sm text-neutral-500">
              +{formatCurrency(strategy.recommended_counter - Number(baseSalary))} from original offer
            </div>
          </div>

          {/* Justification Points */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Justification Points</h3>
            <ul className="space-y-3">
              {strategy.justification_points.map((point, idx) => (
                <li key={idx} className="flex items-start gap-3 text-neutral-300">
                  <span className="w-6 h-6 bg-primary-500/20 text-primary-400 rounded-full flex items-center justify-center text-sm flex-shrink-0">
                    {idx + 1}
                  </span>
                  {point}
                </li>
              ))}
            </ul>
          </div>

          {/* Scripts */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Ready-to-Use Scripts</h3>
            <div className="space-y-4">
              {scripts.map((script) => (
                <div key={script.id} className="border border-neutral-700 rounded-xl overflow-hidden">
                  <button
                    onClick={() => setExpandedScript(expandedScript === script.id ? null : script.id)}
                    className="w-full flex items-center justify-between p-4 bg-neutral-800/50 hover:bg-neutral-800 transition-colors"
                  >
                    <span className="font-medium">{script.title}</span>
                    {expandedScript === script.id ? (
                      <ChevronUp className="w-5 h-5" />
                    ) : (
                      <ChevronDown className="w-5 h-5" />
                    )}
                  </button>
                  {expandedScript === script.id && (
                    <div className="p-4 bg-neutral-900/50">
                      <pre className="whitespace-pre-wrap text-sm text-neutral-300 font-sans">
                        {script.content}
                      </pre>
                      <button
                        onClick={() => copyToClipboard(script.content, script.id)}
                        className="mt-4 flex items-center gap-2 px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-sm transition-colors"
                      >
                        <Copy className="w-4 h-4" />
                        {copiedScript === script.id ? "Copied!" : "Copy to Clipboard"}
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Fallback Positions */}
          {strategy.scripts.fallback_positions.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4">Fallback Positions</h3>
              <p className="text-sm text-neutral-400 mb-3">
                If they can&apos;t meet your salary ask, consider negotiating for:
              </p>
              <div className="flex flex-wrap gap-2">
                {strategy.scripts.fallback_positions.map((pos, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 bg-neutral-800 border border-neutral-700 rounded-full text-sm"
                  >
                    {pos}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Timing & Risk */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-3">Timing Advice</h3>
              <p className="text-neutral-300">{strategy.timing_advice}</p>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-3">Risk Assessment</h3>
              <p className="text-neutral-300">{strategy.risk_assessment}</p>
            </div>
          </div>

          {/* Alternative Asks */}
          {strategy.alternative_asks.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4">Alternative Things to Ask For</h3>
              <ul className="grid md:grid-cols-2 gap-2">
                {strategy.alternative_asks.map((ask, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-sm text-neutral-300">
                    <CheckCircle className="w-4 h-4 text-primary-400" />
                    {ask}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Start Over */}
          <div className="flex gap-4">
            <Link
              href="/dashboard/tools"
              className="flex-1 py-3 bg-neutral-800 hover:bg-neutral-700 rounded-xl font-medium transition-colors text-center"
            >
              Back to Tools
            </Link>
            <button
              onClick={() => {
                setPhase("input");
                setAnalysis(null);
                setStrategy(null);
              }}
              className="flex-1 py-3 bg-primary-600 hover:bg-primary-500 rounded-xl font-medium transition-colors"
            >
              Analyze Another Offer
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
