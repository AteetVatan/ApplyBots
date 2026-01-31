"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Send,
  Loader2,
  Bot,
  User,
  CheckCircle,
  XCircle,
  AlertCircle,
  Trophy,
  Target,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import {
  api,
  InterviewQuestion,
  AnswerFeedback,
  InterviewSummary,
  InterviewType,
  ExperienceLevel,
} from "@/lib/api";

type Phase = "setup" | "interview" | "summary";

interface Message {
  id: string;
  type: "question" | "answer" | "feedback";
  content: string;
  question?: InterviewQuestion;
  feedback?: AnswerFeedback;
}

export default function InterviewRoleplayPage() {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("setup");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Setup form state
  const [targetRole, setTargetRole] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [interviewType, setInterviewType] = useState<InterviewType>("mixed");
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel>("mid");

  // Interview state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [questionsRemaining, setQuestionsRemaining] = useState(0);
  const [currentScore, setCurrentScore] = useState(0);
  const [answer, setAnswer] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  // Summary state
  const [summary, setSummary] = useState<InterviewSummary | null>(null);

  const startInterview = async () => {
    if (!targetRole.trim()) {
      setError("Please enter a target role");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.startInterview({
        target_role: targetRole,
        company_name: companyName || undefined,
        interview_type: interviewType,
        experience_level: experienceLevel,
      });

      setSessionId(response.session_id);
      setCurrentQuestion(response.first_question);
      setQuestionsRemaining(response.total_questions - 1);

      setMessages([
        {
          id: "q_0",
          type: "question",
          content: response.first_question.question_text,
          question: response.first_question,
        },
      ]);

      setPhase("interview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start interview");
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim() || !sessionId || !currentQuestion) return;

    setIsLoading(true);
    const userAnswer = answer;
    setAnswer("");

    // Add answer to messages
    setMessages((prev) => [
      ...prev,
      {
        id: `a_${currentQuestion.question_id}`,
        type: "answer",
        content: userAnswer,
      },
    ]);

    try {
      const response = await api.respondToInterview({
        session_id: sessionId,
        question_id: currentQuestion.question_id,
        answer: userAnswer,
      });

      // Add feedback to messages
      setMessages((prev) => [
        ...prev,
        {
          id: `f_${currentQuestion.question_id}`,
          type: "feedback",
          content: "",
          feedback: response.feedback,
        },
      ]);

      setCurrentScore(response.current_score);
      setQuestionsRemaining(response.questions_remaining);

      if (response.next_question) {
        setCurrentQuestion(response.next_question);
        // Add next question after a brief delay
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            {
              id: `q_${response.next_question!.question_id}`,
              type: "question",
              content: response.next_question!.question_text,
              question: response.next_question!,
            },
          ]);
        }, 500);
      } else {
        // Interview complete, get summary
        await endInterview();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit answer");
    } finally {
      setIsLoading(false);
    }
  };

  const endInterview = async () => {
    if (!sessionId) return;

    setIsLoading(true);
    try {
      const response = await api.endInterview(sessionId);
      setSummary(response.summary);
      setPhase("summary");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to end interview");
    } finally {
      setIsLoading(false);
    }
  };

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case "excellent":
        return "text-emerald-400";
      case "good":
        return "text-primary-400";
      case "needs_improvement":
        return "text-amber-400";
      case "poor":
        return "text-red-400";
      default:
        return "text-neutral-400";
    }
  };

  const getRatingIcon = (rating: string) => {
    switch (rating) {
      case "excellent":
        return <Trophy className="w-5 h-5 text-emerald-400" />;
      case "good":
        return <CheckCircle className="w-5 h-5 text-primary-400" />;
      case "needs_improvement":
        return <AlertCircle className="w-5 h-5 text-amber-400" />;
      case "poor":
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return null;
    }
  };

  // Setup Phase
  if (phase === "setup") {
    return (
      <div className="max-w-2xl mx-auto">
        <Link
          href="/dashboard/tools"
          className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Tools
        </Link>

        <div className="glass-card p-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <Bot className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h1 className="text-2xl font-display font-bold">Interview Roleplay</h1>
              <p className="text-neutral-400">Practice with AI-powered mock interviews</p>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium mb-2">Target Role *</label>
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g., Senior Software Engineer"
                className="w-full px-4 py-3 bg-neutral-800 border border-neutral-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Company (Optional)</label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g., Google, Meta, Startup"
                className="w-full px-4 py-3 bg-neutral-800 border border-neutral-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Interview Type</label>
                <select
                  value={interviewType}
                  onChange={(e) => setInterviewType(e.target.value as InterviewType)}
                  className="w-full px-4 py-3 bg-neutral-800 border border-neutral-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                >
                  <option value="mixed">Mixed</option>
                  <option value="behavioral">Behavioral</option>
                  <option value="technical">Technical</option>
                  <option value="situational">Situational</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Experience Level</label>
                <select
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value as ExperienceLevel)}
                  className="w-full px-4 py-3 bg-neutral-800 border border-neutral-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                >
                  <option value="entry">Entry Level</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior</option>
                  <option value="lead">Lead/Staff</option>
                  <option value="executive">Executive</option>
                </select>
              </div>
            </div>

            <button
              onClick={startInterview}
              disabled={isLoading || !targetRole.trim()}
              className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-600/50 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  Start Interview
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Summary Phase
  if (phase === "summary" && summary) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="glass-card p-8">
          <div className="text-center mb-8">
            <div className="w-20 h-20 rounded-full bg-primary-500/20 flex items-center justify-center mx-auto mb-4">
              <Trophy className="w-10 h-10 text-primary-400" />
            </div>
            <h1 className="text-3xl font-display font-bold mb-2">Interview Complete!</h1>
            <p className="text-neutral-400">
              Here&apos;s how you did in your {summary.target_role} interview
            </p>
          </div>

          {/* Score Card */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="glass-card p-4 text-center">
              <div className="text-3xl font-bold text-primary-400">{summary.overall_score.toFixed(1)}</div>
              <div className="text-sm text-neutral-400">Overall Score</div>
            </div>
            <div className="glass-card p-4 text-center">
              <div className="text-3xl font-bold">{summary.questions_answered}</div>
              <div className="text-sm text-neutral-400">Questions</div>
            </div>
            <div className="glass-card p-4 text-center">
              <div className={`text-3xl font-bold ${getRatingColor(summary.overall_rating)}`}>
                {summary.overall_rating.replace("_", " ")}
              </div>
              <div className="text-sm text-neutral-400">Rating</div>
            </div>
          </div>

          {/* Strengths & Improvements */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-400" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {summary.strengths.map((strength, idx) => (
                  <li key={idx} className="text-sm text-neutral-300 flex items-start gap-2">
                    <span className="text-emerald-400 mt-1">•</span>
                    {strength}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <Target className="w-5 h-5 text-amber-400" />
                Areas to Improve
              </h3>
              <ul className="space-y-2">
                {summary.areas_to_improve.map((area, idx) => (
                  <li key={idx} className="text-sm text-neutral-300 flex items-start gap-2">
                    <span className="text-amber-400 mt-1">•</span>
                    {area}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Recommendations */}
          {summary.recommendations.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-3">Recommendations</h3>
              <ul className="space-y-2">
                {summary.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-neutral-400 flex items-start gap-2">
                    <span className="text-primary-400 font-bold">{idx + 1}.</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => {
                setPhase("setup");
                setMessages([]);
                setSessionId(null);
                setSummary(null);
              }}
              className="flex-1 py-3 bg-primary-600 hover:bg-primary-500 rounded-xl font-medium transition-colors"
            >
              Practice Again
            </button>
            <Link
              href="/dashboard/tools"
              className="flex-1 py-3 bg-neutral-800 hover:bg-neutral-700 rounded-xl font-medium transition-colors text-center"
            >
              Back to Tools
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Interview Phase
  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-display font-bold">{targetRole} Interview</h1>
          <p className="text-sm text-neutral-400">
            {questionsRemaining + 1} questions remaining • Score: {currentScore.toFixed(1)}/10
          </p>
        </div>
        <button
          onClick={endInterview}
          disabled={isLoading}
          className="px-4 py-2 text-sm bg-neutral-800 hover:bg-neutral-700 rounded-lg transition-colors"
        >
          End Interview
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 glass-card p-4 overflow-y-auto mb-4 space-y-4">
        {messages.map((msg) => {
          if (msg.type === "question") {
            return (
              <div key={msg.id} className="flex gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-emerald-400" />
                </div>
                <div className="flex-1">
                  <div className="bg-neutral-800 p-4 rounded-2xl rounded-tl-sm">
                    <p className="text-white">{msg.content}</p>
                    {msg.question && (
                      <div className="mt-2 flex items-center gap-2 text-xs text-neutral-500">
                        <span className="px-2 py-0.5 bg-neutral-700 rounded">
                          {msg.question.question_type}
                        </span>
                        <span className="px-2 py-0.5 bg-neutral-700 rounded">
                          {msg.question.difficulty}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          }

          if (msg.type === "answer") {
            return (
              <div key={msg.id} className="flex gap-3 justify-end">
                <div className="flex-1 max-w-[80%]">
                  <div className="bg-primary-600 p-4 rounded-2xl rounded-tr-sm">
                    <p className="text-white whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
                <div className="w-10 h-10 rounded-xl bg-primary-500/20 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-primary-400" />
                </div>
              </div>
            );
          }

          if (msg.type === "feedback" && msg.feedback) {
            const fb = msg.feedback;
            return (
              <div key={msg.id} className="flex gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                  {getRatingIcon(fb.rating)}
                </div>
                <div className="flex-1">
                  <div className="bg-neutral-800/50 border border-neutral-700 p-4 rounded-2xl rounded-tl-sm">
                    <div className="flex items-center gap-2 mb-3">
                      <span className={`font-semibold ${getRatingColor(fb.rating)}`}>
                        Score: {fb.score}/10
                      </span>
                      <span className="text-neutral-500">•</span>
                      <span className={`text-sm ${getRatingColor(fb.rating)}`}>
                        {fb.rating.replace("_", " ")}
                      </span>
                    </div>

                    {fb.strengths.length > 0 && (
                      <div className="mb-3">
                        <div className="text-xs text-emerald-400 font-medium mb-1">Strengths</div>
                        <ul className="text-sm text-neutral-300 space-y-1">
                          {fb.strengths.map((s, i) => (
                            <li key={i}>• {s}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {fb.improvements.length > 0 && (
                      <div className="mb-3">
                        <div className="text-xs text-amber-400 font-medium mb-1">To Improve</div>
                        <ul className="text-sm text-neutral-300 space-y-1">
                          {fb.improvements.map((imp, i) => (
                            <li key={i}>• {imp}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {fb.example_answer && (
                      <div>
                        <div className="text-xs text-primary-400 font-medium mb-1">
                          Example Strong Answer
                        </div>
                        <p className="text-sm text-neutral-400 italic">{fb.example_answer}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          }

          return null;
        })}

        {isLoading && (
          <div className="flex gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" />
            </div>
            <div className="bg-neutral-800 p-4 rounded-2xl rounded-tl-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce delay-100" />
                <span className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="glass-card p-4">
        <div className="flex items-end gap-3">
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer... (Press Enter to submit)"
            className="flex-1 px-4 py-3 bg-neutral-800 border border-neutral-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all resize-none min-h-[80px]"
            disabled={isLoading}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submitAnswer();
              }
            }}
          />
          <button
            onClick={submitAnswer}
            disabled={!answer.trim() || isLoading}
            className="p-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-600/50 rounded-xl transition-colors"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <p className="text-xs text-neutral-500 mt-2">
          Shift + Enter for new line. Use the STAR method for behavioral questions.
        </p>
      </div>
    </div>
  );
}
