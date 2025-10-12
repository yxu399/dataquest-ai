import { Card } from "@/components/ui/card"
import { BarChart3, TrendingUp, Activity, MessageSquare } from "lucide-react"

export function DataVisualization() {
  const data = [
    { month: 'Jan', value: 32000, label: '$32K' },
    { month: 'Feb', value: 41000, label: '$41K' },
    { month: 'Mar', value: 35000, label: '$35K' },
    { month: 'Apr', value: 48000, label: '$48K' },
    { month: 'May', value: 52000, label: '$52K' },
    { month: 'Jun', value: 58000, label: '$58K' },
  ]
  const maxValue = Math.max(...data.map(d => d.value))

  return (
    <div className="relative pb-8">
      {/* Background glow effect */}
      <div className="absolute -inset-4 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-3xl blur-3xl" />

      {/* Main visualization card */}
      <Card className="relative overflow-visible border shadow-2xl bg-card">
        <div className="p-8 space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-xl">Revenue Overview</h3>
              <p className="text-sm text-muted-foreground mt-1">Last 6 months</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400">
              <TrendingUp className="h-4 w-4" />
              <span className="text-sm font-semibold">+81%</span>
            </div>
          </div>

          {/* Bar chart visualization */}
          <div className="space-y-4">
            <div className="flex items-end justify-between gap-4 h-56 border-b border-l border-border/50 pb-4 pl-4">
              {data.map((item, i) => {
                const height = (item.value / maxValue) * 100
                return (
                  <div key={i} className="flex flex-col items-center gap-3 flex-1 group">
                    <div className="w-full flex flex-col items-center justify-end" style={{ height: '200px' }}>
                      <span className="text-xs font-medium text-muted-foreground mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        {item.label}
                      </span>
                      <div
                        className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-lg transition-all duration-700 hover:from-blue-700 hover:to-blue-500 shadow-lg shadow-blue-500/20 cursor-pointer"
                        style={{
                          height: `${height}%`,
                          animation: `slideUp 0.8s ease-out ${i * 0.1}s both`
                        }}
                      />
                    </div>
                    <span className="text-xs font-medium text-foreground">
                      {item.month}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Stats cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/50 dark:to-indigo-950/50 p-4 border border-blue-100 dark:border-blue-900/50">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                <span className="text-xs font-semibold text-blue-900 dark:text-blue-100">Total Revenue</span>
              </div>
              <p className="text-2xl font-bold text-blue-900 dark:text-blue-50">$266K</p>
            </div>
            <div className="rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/50 dark:to-emerald-950/50 p-4 border border-green-100 dark:border-green-900/50">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-green-600 dark:text-green-400" />
                <span className="text-xs font-semibold text-green-900 dark:text-green-100">Avg Growth</span>
              </div>
              <p className="text-2xl font-bold text-green-900 dark:text-green-50">+13.5%</p>
            </div>
            <div className="rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/50 dark:to-pink-950/50 p-4 border border-purple-100 dark:border-purple-900/50">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                <span className="text-xs font-semibold text-purple-900 dark:text-purple-100">Best Month</span>
              </div>
              <p className="text-2xl font-bold text-purple-900 dark:text-purple-50">June</p>
            </div>
          </div>
        </div>

        {/* Floating chat bubble */}
        <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 max-w-sm w-full px-4">
          <div className="bg-gradient-to-br from-white to-blue-50 dark:from-gray-900 dark:to-blue-950 border-2 border-blue-200 dark:border-blue-800 rounded-2xl shadow-2xl p-5 animate-float">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white">
                <MessageSquare className="h-4 w-4" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-foreground mb-1">"Show me revenue trends"</p>
                <p className="text-xs text-muted-foreground mb-2">
                  AI analyzing your data...
                </p>
                <div className="flex gap-1.5">
                  <div className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
                  <div className="h-2 w-2 rounded-full bg-blue-600 animate-pulse delay-100" />
                  <div className="h-2 w-2 rounded-full bg-blue-600 animate-pulse delay-200" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <style>{`
        @keyframes slideUp {
          from {
            height: 0%;
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        .animate-float {
          animation: float 3s ease-in-out infinite;
        }

        .delay-100 {
          animation-delay: 0.1s;
        }

        .delay-200 {
          animation-delay: 0.2s;
        }
      `}</style>
    </div>
  )
}
