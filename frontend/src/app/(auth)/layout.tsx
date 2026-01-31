import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-neutral-950 flex flex-col">
      {/* Header */}
      <header className="py-6 px-6">
        <Link href="/" className="text-2xl font-display font-bold gradient-text">
          ApplyBots
        </Link>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center px-6 pb-12">
        {children}
      </main>

      {/* Background gradient */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-br from-primary-950/30 via-neutral-950 to-accent-950/20" />
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_center,rgba(51,112,255,0.1),transparent_70%)]" />
    </div>
  );
}
