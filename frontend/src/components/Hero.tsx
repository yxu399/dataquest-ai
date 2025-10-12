import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles } from "lucide-react"
import { DataVisualization } from "@/components/DataVisualization"

export function Hero() {
  return (
    <section className="container mx-auto px-4 pt-32 pb-20">
      <div className="grid items-center gap-12 lg:grid-cols-2">
        <div className="flex flex-col gap-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary w-fit">
            <Sparkles className="h-4 w-4" />
            AI-Powered Analysis
          </div>

          <h1 className="font-sans text-5xl font-bold leading-tight tracking-tight text-balance lg:text-6xl">
            Talk to your data like never before
          </h1>

          <p className="text-lg leading-relaxed text-muted-foreground text-pretty max-w-xl">
            DataQuest transforms complex data analysis into simple conversations. Ask questions in plain English and get
            instant insights, visualizations, and actionable answers.
          </p>

          <div className="flex flex-col gap-4 sm:flex-row">
            <Link to="/app">
              <Button size="lg" className="gap-2">
                Start analyzing now
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              No coding required
            </div>
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              Instant insights
            </div>
          </div>
        </div>

        <div className="relative">
          <DataVisualization />
        </div>
      </div>
    </section>
  )
}
