export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-4">
          Decomposition Pipeline Control Center
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Real-time control center for the LangGraph decomposition pipeline
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Pipeline Status</h2>
            <p className="text-muted-foreground">
              Monitor real-time pipeline progress and stage completion
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Decomposition View</h2>
            <p className="text-muted-foreground">
              Interactive graph visualization of problem decomposition
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Agent Pools</h2>
            <p className="text-muted-foreground">
              Monitor agent activity across specialized pools
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Human Review</h2>
            <p className="text-muted-foreground">
              Approve, reject, or modify decisions at approval gates
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Technique Catalog</h2>
            <p className="text-muted-foreground">
              Browse algorithmic decomposition techniques
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Export & Analysis</h2>
            <p className="text-muted-foreground">
              Export results and view detailed metrics
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
