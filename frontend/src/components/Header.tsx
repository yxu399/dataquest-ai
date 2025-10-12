import { Link } from "react-router-dom"
import { MessageSquare } from "lucide-react"

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-lg">
      <div className="container mx-auto flex items-center justify-between px-4 py-4">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <MessageSquare className="h-6 w-6 text-primary" />
          <span className="font-sans text-xl font-semibold">DataQuest</span>
        </Link>

        <nav className="flex items-center gap-8">
          <a
            href="#features"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Features
          </a>
          <a
            href="#how-it-works"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            How it works
          </a>
        </nav>
      </div>
    </header>
  )
}
