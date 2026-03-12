import Dashboard from "@/components/Dashboard";

export default function Home() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Abstract glowing orbs in background */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 opacity-30">
        <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-[var(--color-neon-blue)] rounded-full blur-[150px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-[var(--color-neon-purple)] rounded-full blur-[150px]" />
      </div>
      
      <Dashboard />
    </div>
  );
}
