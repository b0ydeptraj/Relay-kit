import { Reveal } from "@/components/reveal";

interface CommandPanelProps {
  label: string;
  title: string;
  body: string;
  example: string;
  note: string;
  delay?: number;
  variant?: "night" | "paper";
  compact?: boolean;
}

export function CommandPanel({
  label,
  title,
  body,
  example,
  note,
  delay = 0,
  variant = "night",
  compact = false,
}: CommandPanelProps) {
  return (
    <Reveal delay={delay} className={`command-card command-card--${variant}${compact ? " command-card--compact" : ""}`}>
      <span className="command-card__badge">{label}</span>
      <h3>{title}</h3>
      <p>{body}</p>
      <div className="command-card__example">
        <span>Example</span>
        <code>{example}</code>
      </div>
      <small>{note}</small>
    </Reveal>
  );
}
