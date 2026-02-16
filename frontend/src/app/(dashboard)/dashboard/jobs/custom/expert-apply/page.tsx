"use client";

import { useState } from "react";
import Link from "next/link";
import {
    ArrowLeft,
    Loader2,
    Sparkles,
    FileText,
    CheckCircle,
    AlertCircle,
    ChevronRight,
    Target,
    BookOpen,
    Shield,
    ClipboardPaste,
} from "lucide-react";
import {
    useCareerKitResumes,
    useAnalyze,
    useGenerate,
    type ResumeSource,
    type CustomJD,
    type AnalyzeResponse,
    type GenerateResponse,
    type QuestionnaireAnswer,
    type GapMapItem,
} from "@/hooks/useCareerKit";

type Phase = "input" | "select-resume" | "analyzing" | "questionnaire" | "generating" | "results";

function GapStatusBadge({ status }: { status: GapMapItem["status"] }) {
    const config = {
        covered: { color: "bg-emerald-500/20 text-emerald-400", label: "Covered" },
        partial: { color: "bg-amber-500/20 text-amber-400", label: "Partial" },
        missing: { color: "bg-red-500/20 text-red-400", label: "Missing" },
        unclear: { color: "bg-neutral-500/20 text-neutral-400", label: "Unclear" },
    };
    const c = config[status] || config.unclear;
    return <span className={`text-xs px-2 py-0.5 rounded-full ${c.color}`}>{c.label}</span>;
}

export default function CustomExpertApplyPage() {
    const { data: resumes, isLoading: resumesLoading } = useCareerKitResumes();
    const analyze = useAnalyze();
    const generate = useGenerate();

    const [phase, setPhase] = useState<Phase>("input");
    const [customJD, setCustomJD] = useState<CustomJD>({
        title: "",
        company: "",
        description: "",
        location: "",
        url: "",
    });
    const [selectedResume, setSelectedResume] = useState<ResumeSource | null>(null);
    const [analysisResult, setAnalysisResult] = useState<AnalyzeResponse | null>(null);
    const [generationResult, setGenerationResult] = useState<GenerateResponse | null>(null);
    const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
    const [error, setError] = useState<string | null>(null);

    const proceedToResumes = () => {
        if (!customJD.title.trim() || !customJD.description.trim()) {
            setError("Please fill in at least the job title and description");
            return;
        }
        setError(null);
        setPhase("select-resume");
    };

    const startAnalysis = async () => {
        if (!selectedResume) return;
        setPhase("analyzing");
        setError(null);
        try {
            const result = await analyze.mutateAsync({
                custom_jd: customJD,
                resume_source: selectedResume,
            });
            setAnalysisResult(result);
            if (result.questionnaire.length > 0) {
                setPhase("questionnaire");
            } else {
                await generateResults(result.session_id);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Analysis failed");
            setPhase("select-resume");
        }
    };

    const generateResults = async (sessionId?: string) => {
        const sid = sessionId || analysisResult?.session_id;
        if (!sid) return;
        setPhase("generating");
        setError(null);
        try {
            const formattedAnswers: QuestionnaireAnswer[] = Object.entries(answers).map(
                ([question_id, answer]) => ({ question_id, answer })
            );
            const result = await generate.mutateAsync({
                session_id: sid,
                answers: formattedAnswers,
            });
            setGenerationResult(result);
            setPhase("results");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Generation failed");
            setPhase("questionnaire");
        }
    };

    const updateAnswer = (questionId: string, value: string | string[]) => {
        setAnswers((prev) => ({ ...prev, [questionId]: value }));
    };

    const allResumes = [
        ...(resumes?.uploaded_resumes || []).map((r) => ({ ...r, source_type: "uploaded" as const })),
        ...(resumes?.builder_drafts || []).map((r) => ({ ...r, source_type: "draft" as const })),
    ];

    // Input Phase — paste external JD
    if (phase === "input") {
        return (
            <div className="max-w-2xl mx-auto">
                <Link
                    href="/dashboard/jobs"
                    className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Jobs
                </Link>

                <div className="glass-card p-8">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-primary-500/20 flex items-center justify-center">
                            <ClipboardPaste className="w-6 h-6 text-purple-400" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-display font-bold">Paste External JD</h1>
                            <p className="text-neutral-400">Tailor your resume to any job description</p>
                        </div>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Job Title *</label>
                                <input
                                    type="text"
                                    value={customJD.title}
                                    onChange={(e) => setCustomJD((prev) => ({ ...prev, title: e.target.value }))}
                                    placeholder="e.g., Senior Software Engineer"
                                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Company</label>
                                <input
                                    type="text"
                                    value={customJD.company}
                                    onChange={(e) => setCustomJD((prev) => ({ ...prev, company: e.target.value }))}
                                    placeholder="e.g., Google"
                                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Location</label>
                                <input
                                    type="text"
                                    value={customJD.location || ""}
                                    onChange={(e) => setCustomJD((prev) => ({ ...prev, location: e.target.value }))}
                                    placeholder="e.g., San Francisco, CA"
                                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Job URL</label>
                                <input
                                    type="url"
                                    value={customJD.url || ""}
                                    onChange={(e) => setCustomJD((prev) => ({ ...prev, url: e.target.value }))}
                                    placeholder="https://..."
                                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">Job Description *</label>
                            <textarea
                                value={customJD.description}
                                onChange={(e) => setCustomJD((prev) => ({ ...prev, description: e.target.value }))}
                                rows={10}
                                placeholder="Paste the full job description here..."
                                className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                            />
                        </div>

                        <button
                            onClick={proceedToResumes}
                            disabled={!customJD.title.trim() || !customJD.description.trim()}
                            className="w-full py-4 bg-gradient-to-r from-purple-600 to-primary-600 hover:from-purple-500 hover:to-primary-500 disabled:opacity-50 rounded-xl font-medium transition-all flex items-center justify-center gap-2"
                        >
                            Continue
                            <ChevronRight className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Select Resume Phase
    if (phase === "select-resume") {
        return (
            <div className="max-w-2xl mx-auto">
                <button
                    onClick={() => setPhase("input")}
                    className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back to JD
                </button>

                <div className="glass-card p-8">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 flex items-center justify-center">
                            <Sparkles className="w-6 h-6 text-primary-400" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-display font-bold">Select Resume</h1>
                            <p className="text-neutral-400">
                                Tailoring for: {customJD.title}
                                {customJD.company && ` at ${customJD.company}`}
                            </p>
                        </div>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <div className="space-y-3 mb-6">
                        {resumesLoading ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="w-6 h-6 animate-spin text-primary-400" />
                            </div>
                        ) : allResumes.length === 0 ? (
                            <div className="text-center py-8 text-neutral-400">
                                <FileText className="w-10 h-10 mx-auto mb-3 opacity-50" />
                                <p>No resumes found. Upload one first.</p>
                                <Link
                                    href="/dashboard/resumes"
                                    className="inline-block mt-3 text-primary-400 hover:text-primary-300"
                                >
                                    Go to Resumes →
                                </Link>
                            </div>
                        ) : (
                            allResumes.map((resume) => (
                                <button
                                    key={resume.id}
                                    onClick={() =>
                                        setSelectedResume({ source_type: resume.source_type, resume_id: resume.id })
                                    }
                                    className={`w-full text-left p-4 rounded-xl border transition-all ${selectedResume?.resume_id === resume.id
                                            ? "border-primary-500 bg-primary-500/10"
                                            : "border-neutral-700 bg-neutral-800/50 hover:border-neutral-600"
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <FileText className="w-5 h-5 text-neutral-400" />
                                            <div>
                                                <div className="font-medium">{resume.name}</div>
                                                <div className="text-xs text-neutral-500">
                                                    {resume.source_type === "uploaded" ? "Uploaded" : "Builder Draft"}
                                                    {resume.is_primary && " • Primary"}
                                                </div>
                                            </div>
                                        </div>
                                        {selectedResume?.resume_id === resume.id && (
                                            <CheckCircle className="w-5 h-5 text-primary-400" />
                                        )}
                                    </div>
                                </button>
                            ))
                        )}
                    </div>

                    <button
                        onClick={startAnalysis}
                        disabled={!selectedResume}
                        className="w-full py-4 bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-500 hover:to-purple-500 disabled:opacity-50 rounded-xl font-medium transition-all flex items-center justify-center gap-2"
                    >
                        <Sparkles className="w-5 h-5" />
                        Analyze & Tailor Resume
                    </button>
                </div>
            </div>
        );
    }

    // Analyzing Phase
    if (phase === "analyzing") {
        return (
            <div className="max-w-2xl mx-auto">
                <div className="glass-card p-12 text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-primary-400 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold mb-2">Analyzing Job Requirements</h2>
                    <p className="text-neutral-400">
                        Comparing your resume against the job description...
                    </p>
                </div>
            </div>
        );
    }

    // Questionnaire Phase
    if (phase === "questionnaire" && analysisResult) {
        return (
            <div className="max-w-3xl mx-auto">
                <button
                    onClick={() => setPhase("select-resume")}
                    className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back
                </button>

                <div className="space-y-6">
                    {/* Gap Map */}
                    <div className="glass-card p-6">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Target className="w-5 h-5 text-amber-400" />
                            Gap Analysis
                        </h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {["covered", "partial", "missing", "unclear"].map((status) => {
                                const count = analysisResult.gap_map.filter((g) => g.status === status).length;
                                return (
                                    <div key={status} className="text-center p-3 bg-neutral-800/50 rounded-xl">
                                        <div className="text-2xl font-bold">{count}</div>
                                        <GapStatusBadge status={status as GapMapItem["status"]} />
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Questions */}
                    {analysisResult.questionnaire.length > 0 && (
                        <div className="glass-card p-6">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <BookOpen className="w-5 h-5 text-primary-400" />
                                Help Us Fill the Gaps
                            </h2>

                            {error && (
                                <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                                    {error}
                                </div>
                            )}

                            <div className="space-y-5">
                                {analysisResult.questionnaire.map((q) => (
                                    <div key={q.id}>
                                        <label className="block text-sm font-medium mb-1">{q.question}</label>
                                        <p className="text-xs text-neutral-500 mb-2">{q.why_asked}</p>
                                        {q.answer_type === "text" && (
                                            <textarea
                                                value={(answers[q.id] as string) || ""}
                                                onChange={(e) => updateAnswer(q.id, e.target.value)}
                                                rows={3}
                                                className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                                            />
                                        )}
                                        {q.answer_type === "yes_no" && (
                                            <div className="flex gap-3">
                                                {["Yes", "No"].map((opt) => (
                                                    <button
                                                        key={opt}
                                                        onClick={() => updateAnswer(q.id, opt.toLowerCase())}
                                                        className={`px-4 py-2 rounded-lg border transition-all ${answers[q.id] === opt.toLowerCase()
                                                                ? "border-primary-500 bg-primary-500/10"
                                                                : "border-neutral-700 bg-neutral-800"
                                                            }`}
                                                    >
                                                        {opt}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                        {q.answer_type === "multi_select" && q.options && (
                                            <div className="flex flex-wrap gap-2">
                                                {q.options.map((opt) => {
                                                    const selected = ((answers[q.id] as string[]) || []).includes(opt);
                                                    return (
                                                        <button
                                                            key={opt}
                                                            onClick={() => {
                                                                const current = (answers[q.id] as string[]) || [];
                                                                updateAnswer(
                                                                    q.id,
                                                                    selected ? current.filter((s) => s !== opt) : [...current, opt]
                                                                );
                                                            }}
                                                            className={`px-3 py-1.5 rounded-lg border text-sm transition-all ${selected
                                                                    ? "border-primary-500 bg-primary-500/10"
                                                                    : "border-neutral-700 bg-neutral-800"
                                                                }`}
                                                        >
                                                            {opt}
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>

                            <button
                                onClick={() => generateResults()}
                                className="w-full mt-6 py-4 bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-500 hover:to-purple-500 rounded-xl font-medium transition-all flex items-center justify-center gap-2"
                            >
                                <Sparkles className="w-5 h-5" />
                                Generate Tailored Resume
                                <ChevronRight className="w-5 h-5" />
                            </button>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // Generating Phase
    if (phase === "generating") {
        return (
            <div className="max-w-2xl mx-auto">
                <div className="glass-card p-12 text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-purple-400 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold mb-2">Generating Tailored Resume</h2>
                    <p className="text-neutral-400">Creating your optimized resume...</p>
                </div>
            </div>
        );
    }

    // Results Phase
    if (phase === "results" && generationResult) {
        const cv = generationResult.tailored_cv;
        const prep = generationResult.interview_prep;

        return (
            <div className="max-w-4xl mx-auto">
                <Link
                    href="/dashboard/jobs"
                    className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Jobs
                </Link>

                <div className="space-y-6">
                    <div className="glass-card p-6 text-center bg-gradient-to-br from-primary-950/30 to-purple-950/30">
                        <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                        <h1 className="text-2xl font-display font-bold mb-1">Tailored Resume Ready</h1>
                        <p className="text-neutral-400">{cv.targeted_title}</p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="glass-card p-6">
                            <h3 className="font-semibold mb-3">Summary</h3>
                            <p className="text-sm text-neutral-300 leading-relaxed">{cv.summary}</p>
                        </div>
                        <div className="glass-card p-6">
                            <h3 className="font-semibold mb-3">Skills</h3>
                            <div className="flex flex-wrap gap-2">
                                {cv.skills.map((skill, idx) => (
                                    <span key={idx} className="px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full text-sm">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>

                    {Object.entries(cv.experience_bullets).length > 0 && (
                        <div className="glass-card p-6">
                            <h3 className="font-semibold mb-4 flex items-center gap-2">
                                <FileText className="w-5 h-5 text-primary-400" />
                                Tailored Experience
                            </h3>
                            {Object.entries(cv.experience_bullets).map(([role, bullets]) => (
                                <div key={role} className="mb-4 last:mb-0">
                                    <h4 className="text-sm font-medium text-neutral-300 mb-2">{role}</h4>
                                    <ul className="space-y-1.5">
                                        {bullets.map((bullet, idx) => (
                                            <li key={idx} className="flex items-start gap-2 text-sm text-neutral-400">
                                                <span className="text-primary-400 mt-0.5">•</span>
                                                <span>{bullet.text}</span>
                                                {bullet.needs_verification && (
                                                    <AlertCircle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
                                                )}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                    )}

                    {cv.truth_notes.length > 0 && (
                        <div className="glass-card p-6 border-amber-500/20">
                            <h3 className="font-semibold mb-3 flex items-center gap-2">
                                <Shield className="w-5 h-5 text-amber-400" />
                                Truth Notes
                            </h3>
                            <ul className="space-y-1">
                                {cv.truth_notes.map((note, idx) => (
                                    <li key={idx} className="text-sm text-amber-300 flex items-start gap-2">
                                        <span className="mt-0.5">⚠</span>
                                        {note}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {prep && (
                        <div className="glass-card p-6">
                            <h3 className="font-semibold mb-4 flex items-center gap-2">
                                <Target className="w-5 h-5 text-emerald-400" />
                                Interview Prep
                            </h3>
                            <p className="text-sm text-neutral-300 mb-4">{prep.role_understanding}</p>
                            {prep.likely_questions.length > 0 && (
                                <div className="space-y-3">
                                    <h4 className="text-sm font-medium text-neutral-400">Likely Questions</h4>
                                    {prep.likely_questions.slice(0, 5).map((q, idx) => (
                                        <div key={idx} className="p-3 bg-neutral-800/50 rounded-lg">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-xs px-2 py-0.5 bg-neutral-700 rounded">{q.category}</span>
                                                <span className="text-xs px-2 py-0.5 bg-neutral-700 rounded">{q.difficulty}</span>
                                            </div>
                                            <p className="text-sm">{q.question}</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    <div className="flex gap-4">
                        <Link href="/dashboard/jobs" className="flex-1 py-3 bg-neutral-800 hover:bg-neutral-700 rounded-xl font-medium transition-colors text-center">
                            Back to Jobs
                        </Link>
                        <Link href="/dashboard/applications" className="flex-1 py-3 bg-primary-600 hover:bg-primary-500 rounded-xl font-medium transition-colors text-center">
                            View Applications
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    return null;
}
