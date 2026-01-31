"use client";

import Link from "next/link";
import { MessageSquare, DollarSign, Compass, ArrowRight, Sparkles } from "lucide-react";

interface ToolCardProps {
  href: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  features: string[];
  accentColor: string;
}

function ToolCard({ href, icon, title, description, features, accentColor }: ToolCardProps) {
  return (
    <Link
      href={href}
      className="group glass-card p-6 hover:border-primary-500/30 transition-all duration-300 flex flex-col"
    >
      <div
        className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-5 transition-transform group-hover:scale-110 ${accentColor}`}
      >
        {icon}
      </div>
      
      <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-400 transition-colors">
        {title}
      </h3>
      
      <p className="text-neutral-400 text-sm mb-4 flex-grow">
        {description}
      </p>
      
      <ul className="space-y-2 mb-5">
        {features.map((feature, idx) => (
          <li key={idx} className="text-sm text-neutral-500 flex items-center gap-2">
            <Sparkles className="w-3 h-3 text-primary-500" />
            {feature}
          </li>
        ))}
      </ul>
      
      <div className="flex items-center text-primary-400 text-sm font-medium group-hover:gap-2 transition-all">
        Get Started
        <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
      </div>
    </Link>
  );
}

export default function ToolsPage() {
  const tools: ToolCardProps[] = [
    {
      href: "/dashboard/tools/interview",
      icon: <MessageSquare className="w-7 h-7" />,
      title: "Interview Roleplay",
      description: "Practice with AI-powered mock interviews tailored to your target role. Get instant feedback on your answers.",
      features: [
        "Behavioral & technical questions",
        "Real-time feedback & scoring",
        "Personalized to your resume",
      ],
      accentColor: "bg-emerald-500/20 text-emerald-400",
    },
    {
      href: "/dashboard/tools/negotiation",
      icon: <DollarSign className="w-7 h-7" />,
      title: "Offer Negotiation Advisor",
      description: "Get strategic advice on salary negotiations. Analyze offers and craft winning counter-proposals.",
      features: [
        "Market salary comparison",
        "Negotiation scripts & emails",
        "Total compensation analysis",
      ],
      accentColor: "bg-amber-500/20 text-amber-400",
    },
    {
      href: "/dashboard/tools/career",
      icon: <Compass className="w-7 h-7" />,
      title: "Career Advisor",
      description: "Discover your ideal career path. Get personalized recommendations based on your skills and goals.",
      features: [
        "Skill gap analysis",
        "Career path recommendations",
        "Learning roadmap",
      ],
      accentColor: "bg-violet-500/20 text-violet-400",
    },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-display font-bold mb-3">AI Career Tools</h1>
        <p className="text-neutral-400 text-lg">
          Powerful AI assistants to help you prepare for interviews, negotiate offers, 
          and plan your career journey.
        </p>
      </div>

      {/* Tools Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {tools.map((tool) => (
          <ToolCard key={tool.href} {...tool} />
        ))}
      </div>

      {/* Tips Section */}
      <div className="mt-12 glass-card p-6 bg-gradient-to-br from-primary-950/30 to-transparent">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary-400" />
          Pro Tips
        </h2>
        <ul className="grid md:grid-cols-2 gap-4 text-sm text-neutral-400">
          <li className="flex items-start gap-2">
            <span className="text-primary-400 font-bold">1.</span>
            Upload your resume first for personalized interview questions and career advice.
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-400 font-bold">2.</span>
            Practice multiple interview sessions to build confidence before the real thing.
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-400 font-bold">3.</span>
            Use the negotiation advisor before accepting any offer to ensure you&apos;re fairly compensated.
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-400 font-bold">4.</span>
            Review career paths regularly to stay aligned with your long-term goals.
          </li>
        </ul>
      </div>
    </div>
  );
}
