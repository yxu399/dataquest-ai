import { Card } from "@/components/ui/card"
import { Upload, MessageSquare, Sparkles } from "lucide-react"

const steps = [
  {
    icon: Upload,
    title: "Upload CSV file",
    description: "Drop your CSV file to upload. DataQuest automatically analyzes the structure and generates insights.",
    step: "01",
  },
  {
    icon: MessageSquare,
    title: "Chat with your data",
    description: "Ask questions in plain English about trends, correlations, or specific values in your dataset.",
    step: "02",
  },
  {
    icon: Sparkles,
    title: "Get instant visualizations",
    description: "Receive AI-generated charts, statistical analysis, and actionable insights immediately.",
    step: "03",
  },
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-muted/30 py-24">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="font-sans text-4xl font-bold mb-4 text-balance">How it works</h2>
          <p className="text-lg text-muted-foreground text-pretty max-w-2xl mx-auto">
            Get started in minutes. No training required.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
          {steps.map((step, index) => (
            <div key={step.title} className="relative">
              <Card className="p-8 h-full">
                <div className="absolute -top-4 -left-4 rounded-full bg-primary text-primary-foreground w-12 h-12 flex items-center justify-center font-bold text-lg">
                  {step.step}
                </div>
                <div className="rounded-lg bg-primary/10 w-14 h-14 flex items-center justify-center mb-6 mt-4">
                  <step.icon className="h-7 w-7 text-primary" />
                </div>
                <h3 className="font-semibold text-xl mb-3">{step.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{step.description}</p>
              </Card>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-4 w-8 h-0.5 bg-border" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
