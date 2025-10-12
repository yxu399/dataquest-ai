import { Card } from "@/components/ui/card"
import { MessageSquare, BarChart3, Zap, Shield, Database, Sparkles } from "lucide-react"

const features = [
  {
    icon: MessageSquare,
    title: "Natural Language Queries",
    description: "Ask questions in plain English. No SQL, no formulas, just conversation.",
  },
  {
    icon: BarChart3,
    title: "Instant Visualizations",
    description: "Get beautiful charts and graphs automatically generated from your data.",
  },
  {
    icon: Sparkles,
    title: "AI-Powered Insights",
    description: "Powered by Claude 3.5 Sonnet with automatic statistical analysis and correlation detection.",
  },
  {
    icon: Zap,
    title: "Quick CSV Upload",
    description: "Simply upload your CSV file and start analyzing immediately. No setup required.",
  },
]

export function Features() {
  return (
    <section id="features" className="container mx-auto px-4 py-24">
      <div className="text-center mb-16">
        <h2 className="font-sans text-4xl font-bold mb-4 text-balance">Everything you need to understand your data</h2>
        <p className="text-lg text-muted-foreground text-pretty max-w-2xl mx-auto">
          Powerful features that make data analysis accessible to everyone, from beginners to experts.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2 max-w-4xl mx-auto">
        {features.map((feature) => (
          <Card key={feature.title} className="p-6 hover:shadow-lg transition-shadow">
            <div className="rounded-lg bg-primary/10 w-12 h-12 flex items-center justify-center mb-4">
              <feature.icon className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
            <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
          </Card>
        ))}
      </div>
    </section>
  )
}
