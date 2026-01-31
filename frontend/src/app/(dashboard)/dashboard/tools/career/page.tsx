"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Compass,
  Loader2,
  TrendingUp,
  Target,
  BookOpen,
  Users,
  Briefcase,
  ChevronRight,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Clock,
  DollarSign,
  GraduationCap,
} from "lucide-react";
import {
  api,
  CareerAssessResponse,
  CareerPathsResponse,
  CareerPath,
  LearningResource,
} from "@/lib/api";

type Phase = "input" | "assessment" | "paths";

export default function CareerAdvisorPage() {
  const [phase, setPhase] = useState<Phase>("input");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [currentRole, setCurrentRole] = useState("");
  const [yearsInRole, setYearsInRole] = useState(2);
  const [totalExperience, setTotalExperience] = useState(5);
  const [currentIndustry, setCurrentIndustry] = useState("");
  const [skillsInput, setSkillsInput] = useState("");
  const [interestsInput, setInterestsInput] = useState("");
  const [goalsInput, setGoalsInput] = useState("");

  // Paths form
  const [targetIndustriesInput, setTargetIndustriesInput] = useState("");
  const [salaryExpectation, setSalaryExpectation] = useState<number | "">("");
  const [willingToRelocate, setWillingToRelocate] = useState(false);
  const [willingToReskill, setWillingToReskill] = useState(true);
  const [timelineMonths, setTimelineMonths] = useState(12);

  // Results
  const [assessment, setAssessment] = useState<CareerAssessResponse | null>(null);
  const [pathsResponse, setPathsResponse] = useState<CareerPathsResponse | null>(null);

  // UI state
  const [selectedPath, setSelectedPath] = useState<CareerPath | null>(null);

  const parseList = (input: string): string[] => {
    return input
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
  };

  const assessCareer = async () => {
    if (!currentRole || !currentIndustry || !skillsInput) {
      setError("Please fill in required fields");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.assessCareer({
        current_role: currentRole,
        years_in_role: yearsInRole,
        total_experience: totalExperience,
        current_industry: currentIndustry,
        skills: parseList(skillsInput),
        interests: interestsInput ? parseList(interestsInput) : undefined,
        goals: goalsInput ? parseList(goalsInput) : undefined,
      });

      setAssessment(response);
      setPhase("assessment");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to assess career");
    } finally {
      setIsLoading(false);
    }
  };

  const getCareerPaths = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.getCareerPaths({
        current_role: currentRole,
        years_experience: totalExperience,
        skills: parseList(skillsInput),
        target_industries: targetIndustriesInput ? parseList(targetIndustriesInput) : undefined,
        salary_expectation: salaryExpectation ? Number(salaryExpectation) : undefined,
        willing_to_relocate: willingToRelocate,
        willing_to_reskill: willingToReskill,
        timeline_months: timelineMonths,
      });

      setPathsResponse(response);
      setPhase("paths");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate career paths");
    } finally {
      setIsLoading(false);
    }
  };

  const getGrowthColor = (growth: string) => {
    switch (growth) {
      case "high":
        return "text-emerald-400";
      case "low":
        return "text-red-400";
      default:
        return "text-amber-400";
    }
  };

  const getDemandBadge = (demand: string) => {
    const colors = {
      high: "bg-emerald-500/20 text-emerald-400",
      medium: "bg-amber-500/20 text-amber-400",
      low: "bg-red-500/20 text-red-400",
    };
    return colors[demand as keyof typeof colors] || colors.medium;
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "text-red-400 border-red-500/30";
      case "important":
        return "text-amber-400 border-amber-500/30";
      default:
        return "text-neutral-400 border-neutral-600";
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
            <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center">
              <Compass className="w-6 h-6 text-violet-400" />
            </div>
            <div>
              <h1 className="text-2xl font-display font-bold">Career Advisor</h1>
              <p className="text-neutral-400">Discover your ideal career path</p>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-6">
            {/* Current Position */}
            <div>
              <h3 className="text-sm font-medium text-neutral-300 mb-3">Current Position</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Current Role *</label>
                  <input
                    type="text"
                    value={currentRole}
                    onChange={(e) => setCurrentRole(e.target.value)}
                    placeholder="e.g., Software Engineer"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Industry *</label>
                  <input
                    type="text"
                    value={currentIndustry}
                    onChange={(e) => setCurrentIndustry(e.target.value)}
                    placeholder="e.g., Technology, Finance"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Years in Current Role</label>
                  <input
                    type="number"
                    value={yearsInRole}
                    onChange={(e) => setYearsInRole(Number(e.target.value))}
                    min={0}
                    max={50}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Total Years Experience</label>
                  <input
                    type="number"
                    value={totalExperience}
                    onChange={(e) => setTotalExperience(Number(e.target.value))}
                    min={0}
                    max={50}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>

            {/* Skills & Interests */}
            <div>
              <h3 className="text-sm font-medium text-neutral-300 mb-3">Skills & Interests</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Skills * (comma-separated)</label>
                  <textarea
                    value={skillsInput}
                    onChange={(e) => setSkillsInput(e.target.value)}
                    placeholder="e.g., Python, React, Project Management, Data Analysis"
                    rows={2}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Interests (comma-separated)</label>
                  <input
                    type="text"
                    value={interestsInput}
                    onChange={(e) => setInterestsInput(e.target.value)}
                    placeholder="e.g., AI/ML, Leadership, Entrepreneurship"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-neutral-400 mb-1">Career Goals (comma-separated)</label>
                  <input
                    type="text"
                    value={goalsInput}
                    onChange={(e) => setGoalsInput(e.target.value)}
                    placeholder="e.g., Technical leadership, Higher salary, Work-life balance"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={assessCareer}
              disabled={isLoading || !currentRole || !currentIndustry || !skillsInput}
              className="w-full py-4 bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Assess My Career
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Assessment Phase
  if (phase === "assessment" && assessment) {
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
          {/* Growth Potential */}
          <div className="glass-card p-6 text-center">
            <div className="text-sm text-neutral-400 mb-2">Growth Potential</div>
            <div className={`text-3xl font-bold ${getGrowthColor(assessment.growth_potential)}`}>
              {assessment.growth_potential.toUpperCase()}
            </div>
            <p className="text-neutral-400 mt-2">{assessment.market_position}</p>
          </div>

          {/* Strengths & Transferable Skills */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-400" />
                Your Strengths
              </h3>
              <ul className="space-y-2">
                {assessment.strengths.map((s, idx) => (
                  <li key={idx} className="text-sm text-neutral-300 flex items-start gap-2">
                    <span className="text-emerald-400 mt-0.5">•</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary-400" />
                Transferable Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {assessment.transferable_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Skill Assessments */}
          {assessment.skill_assessments.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4">Skill Categories</h3>
              <div className="grid md:grid-cols-2 gap-4">
                {assessment.skill_assessments.map((sa, idx) => (
                  <div
                    key={idx}
                    className="p-4 bg-neutral-800/50 border border-neutral-700 rounded-xl"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{sa.category}</span>
                      <span className={`text-xs px-2 py-0.5 rounded ${getDemandBadge(sa.market_demand)}`}>
                        {sa.market_demand} demand
                      </span>
                    </div>
                    <div className="text-sm text-neutral-400 mb-2">
                      Proficiency: <span className="text-neutral-300">{sa.proficiency}</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {sa.skills.slice(0, 5).map((skill, i) => (
                        <span
                          key={i}
                          className="text-xs px-2 py-0.5 bg-neutral-700 rounded"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Insights */}
          {assessment.key_insights.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-amber-400" />
                Key Insights
              </h3>
              <ul className="space-y-2">
                {assessment.key_insights.map((insight, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-neutral-300">
                    <span className="w-6 h-6 bg-amber-500/20 text-amber-400 rounded-full flex items-center justify-center text-sm flex-shrink-0">
                      {idx + 1}
                    </span>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Get Career Paths */}
          <div className="glass-card p-6 bg-gradient-to-br from-violet-950/30 to-transparent">
            <h3 className="text-lg font-semibold mb-4">Explore Career Paths</h3>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-neutral-400 mb-1">Target Industries (optional)</label>
                <input
                  type="text"
                  value={targetIndustriesInput}
                  onChange={(e) => setTargetIndustriesInput(e.target.value)}
                  placeholder="e.g., AI, Healthcare, Finance"
                  className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm text-neutral-400 mb-1">Salary Expectation</label>
                <input
                  type="number"
                  value={salaryExpectation}
                  onChange={(e) => setSalaryExpectation(e.target.value ? Number(e.target.value) : "")}
                  placeholder="e.g., 150000"
                  className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm text-neutral-400 mb-1">Timeline (months)</label>
                <select
                  value={timelineMonths}
                  onChange={(e) => setTimelineMonths(Number(e.target.value))}
                  className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value={6}>6 months</option>
                  <option value={12}>1 year</option>
                  <option value={24}>2 years</option>
                  <option value={36}>3 years</option>
                </select>
              </div>
              <div className="flex flex-col justify-end gap-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={willingToReskill}
                    onChange={(e) => setWillingToReskill(e.target.checked)}
                    className="w-4 h-4 rounded border-neutral-600 bg-neutral-800 text-primary-500 focus:ring-primary-500"
                  />
                  <span className="text-sm text-neutral-400">Willing to learn new skills</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={willingToRelocate}
                    onChange={(e) => setWillingToRelocate(e.target.checked)}
                    className="w-4 h-4 rounded border-neutral-600 bg-neutral-800 text-primary-500 focus:ring-primary-500"
                  />
                  <span className="text-sm text-neutral-400">Willing to relocate</span>
                </label>
              </div>
            </div>
            <button
              onClick={getCareerPaths}
              disabled={isLoading}
              className="w-full py-3 bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating Paths...
                </>
              ) : (
                <>
                  <Compass className="w-5 h-5" />
                  Explore Career Paths
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Paths Phase
  if (phase === "paths" && pathsResponse) {
    return (
      <div className="max-w-5xl mx-auto">
        <button
          onClick={() => setPhase("assessment")}
          className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Assessment
        </button>

        <div className="space-y-6">
          {/* Career Paths */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Recommended Career Paths</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {pathsResponse.recommended_paths.map((path, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedPath(selectedPath?.target_role === path.target_role ? null : path)}
                  className={`text-left glass-card p-5 transition-all ${
                    selectedPath?.target_role === path.target_role
                      ? "border-primary-500/50 ring-1 ring-primary-500/30"
                      : "hover:border-neutral-600"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-2xl font-bold text-primary-400">{path.fit_score}%</span>
                    <span className="text-xs px-2 py-0.5 bg-neutral-700 rounded">
                      {path.target_industry}
                    </span>
                  </div>
                  <h3 className="font-semibold mb-1">{path.target_role}</h3>
                  <div className="flex items-center gap-4 text-sm text-neutral-400">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {path.time_to_transition_months}mo
                    </span>
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-3 h-3" />
                      {Math.round(path.salary_range_low / 1000)}k-{Math.round(path.salary_range_high / 1000)}k
                    </span>
                  </div>
                  <div className="mt-3 flex items-center text-xs text-primary-400">
                    View details
                    <ChevronRight className="w-3 h-3 ml-1" />
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Selected Path Details */}
          {selectedPath && (
            <div className="glass-card p-6 border-primary-500/30 animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">{selectedPath.target_role}</h3>
                <button
                  onClick={() => setSelectedPath(null)}
                  className="text-neutral-400 hover:text-white"
                >
                  ×
                </button>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Steps */}
                <div>
                  <h4 className="text-sm font-medium text-neutral-300 mb-3">Transition Steps</h4>
                  <ol className="space-y-2">
                    {selectedPath.steps.map((step, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-sm text-neutral-300">
                        <span className="w-5 h-5 bg-primary-500/20 text-primary-400 rounded-full flex items-center justify-center text-xs flex-shrink-0">
                          {idx + 1}
                        </span>
                        {step}
                      </li>
                    ))}
                  </ol>
                </div>

                {/* Skill Gaps */}
                <div>
                  <h4 className="text-sm font-medium text-neutral-300 mb-3 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                    Skill Gaps to Address
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedPath.skill_gaps.map((gap, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-amber-500/20 text-amber-400 rounded-full text-sm"
                      >
                        {gap}
                      </span>
                    ))}
                  </div>

                  {selectedPath.required_certifications.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-neutral-300 mb-2 flex items-center gap-2">
                        <GraduationCap className="w-4 h-4 text-violet-400" />
                        Recommended Certifications
                      </h4>
                      <ul className="text-sm text-neutral-400 space-y-1">
                        {selectedPath.required_certifications.map((cert, idx) => (
                          <li key={idx}>• {cert}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Pros & Cons */}
                <div className="md:col-span-2 grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-emerald-400 mb-2">Pros</h4>
                    <ul className="text-sm text-neutral-300 space-y-1">
                      {selectedPath.pros.map((pro, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                          {pro}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-red-400 mb-2">Cons</h4>
                    <ul className="text-sm text-neutral-300 space-y-1">
                      {selectedPath.cons.map((con, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                          {con}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Learning Roadmap */}
          {pathsResponse.learning_roadmap.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-primary-400" />
                Learning Roadmap
              </h3>
              <div className="grid md:grid-cols-2 gap-3">
                {pathsResponse.learning_roadmap.map((resource, idx) => (
                  <div
                    key={idx}
                    className={`p-4 bg-neutral-800/50 border rounded-xl ${getPriorityColor(resource.priority)}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{resource.skill}</span>
                      <span className="text-xs px-2 py-0.5 bg-neutral-700 rounded capitalize">
                        {resource.priority}
                      </span>
                    </div>
                    <div className="text-sm text-neutral-300">{resource.name}</div>
                    <div className="flex items-center gap-3 mt-2 text-xs text-neutral-500">
                      <span className="capitalize">{resource.resource_type}</span>
                      {resource.provider && <span>• {resource.provider}</span>}
                      <span>• ~{resource.estimated_hours}h</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Wins & Long-term Goals */}
          <div className="grid md:grid-cols-2 gap-6">
            {pathsResponse.quick_wins.length > 0 && (
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-emerald-400" />
                  Quick Wins
                </h3>
                <ul className="space-y-2">
                  {pathsResponse.quick_wins.map((win, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-neutral-300">
                      <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                      {win}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {pathsResponse.long_term_goals.length > 0 && (
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-violet-400" />
                  Long-term Goals
                </h3>
                <ul className="space-y-2">
                  {pathsResponse.long_term_goals.map((goal, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-neutral-300">
                      <Briefcase className="w-4 h-4 text-violet-400 mt-0.5 flex-shrink-0" />
                      {goal}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Networking */}
          {pathsResponse.networking_suggestions.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-primary-400" />
                Networking Suggestions
              </h3>
              <ul className="grid md:grid-cols-2 gap-2">
                {pathsResponse.networking_suggestions.map((suggestion, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-sm text-neutral-300">
                    <ChevronRight className="w-4 h-4 text-primary-400" />
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
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
                setAssessment(null);
                setPathsResponse(null);
                setSelectedPath(null);
              }}
              className="flex-1 py-3 bg-primary-600 hover:bg-primary-500 rounded-xl font-medium transition-colors"
            >
              Start New Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
