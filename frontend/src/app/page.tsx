import Link from "next/link";
import { ArrowRight, Shield, Zap, Users } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-neutral-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-950/50 via-neutral-950 to-accent-950/30" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(51,112,255,0.15),transparent_50%)]" />

        <div className="relative container mx-auto px-6 pt-20 pb-32">
          <nav className="flex items-center justify-between mb-20">
            <div className="text-2xl font-display font-bold gradient-text">
              ApplyBots
            </div>
            <div className="flex items-center gap-6">
              <Link
                href="/login"
                className="text-neutral-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/signup"
                className="px-5 py-2.5 bg-primary-600 hover:bg-primary-500 rounded-xl font-medium transition-colors"
              >
                Get Started
              </Link>
            </div>
          </nav>

          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/20 rounded-full text-primary-400 text-sm mb-8 animate-fade-in">
              <Zap className="w-4 h-4" />
              AI-Powered Job Applications
            </div>

            <h1 className="text-5xl md:text-7xl font-display font-bold text-white mb-6 animate-slide-up">
              Land Your Dream Job
              <br />
              <span className="gradient-text">Without the Grind</span>
            </h1>

            <p className="text-xl text-neutral-400 max-w-2xl mx-auto mb-10 animate-slide-up animation-delay-200">
              Let AI handle the tedious parts of job hunting. We match, apply,
              and track — all while keeping you in control and your information
              truthful.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 animate-slide-up animation-delay-400">
              <Link
                href="/signup"
                className="group px-8 py-4 bg-primary-600 hover:bg-primary-500 rounded-xl font-semibold text-lg transition-all flex items-center gap-2 glow"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="#features"
                className="px-8 py-4 bg-neutral-800 hover:bg-neutral-700 rounded-xl font-semibold text-lg transition-colors border border-neutral-700"
              >
                See How It Works
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 border-t border-neutral-800">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-display font-bold text-center mb-4">
            Why Choose ApplyBots?
          </h2>
          <p className="text-neutral-400 text-center max-w-2xl mx-auto mb-16">
            We built the job application tool we wished existed — fast, honest,
            and respectful of your time.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="Truth-Lock Technology"
              description="Our AI never fabricates. Every claim in your applications is verified against your actual resume."
            />
            <FeatureCard
              icon={<Zap className="w-8 h-8" />}
              title="Smart Matching"
              description="AI analyzes job requirements against your skills, giving you match scores and actionable insights."
            />
            <FeatureCard
              icon={<Users className="w-8 h-8" />}
              title="Human in the Loop"
              description="Review and edit everything before submission. You're always in control."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-b from-neutral-950 to-primary-950/30">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-display font-bold mb-6">
            Ready to Transform Your Job Search?
          </h2>
          <p className="text-neutral-400 max-w-xl mx-auto mb-10">
            Join thousands of job seekers who&apos;ve found their next opportunity
            with ApplyBots.
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 px-8 py-4 bg-accent-500 hover:bg-accent-600 rounded-xl font-semibold text-lg transition-colors"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-neutral-800">
        <div className="container mx-auto px-6 text-center text-neutral-500 text-sm">
          © 2026 ApplyBots. All rights reserved.
        </div>
      </footer>
    </main>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="glass-card p-8 hover:border-primary-500/30 transition-colors group">
      <div className="w-14 h-14 bg-primary-500/10 rounded-xl flex items-center justify-center text-primary-400 mb-6 group-hover:bg-primary-500/20 transition-colors">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-3">{title}</h3>
      <p className="text-neutral-400">{description}</p>
    </div>
  );
}
