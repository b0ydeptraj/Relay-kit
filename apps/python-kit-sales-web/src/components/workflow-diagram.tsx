import { Reveal } from "@/components/reveal";
import { workflowLanes } from "@/content/site";

export function WorkflowDiagram() {
  return (
    <section className="section section--dark" aria-labelledby="workflow-map-title">
      <div className="shell">
        <div className="section-head section-head--dark">
          <p className="eyebrow">Operating lanes</p>
          <h2 id="workflow-map-title">One system, four lanes, clear ownership all the way through verification.</h2>
          <p>
            The page sells process discipline by showing where product, architecture, build, and verification move next.
          </p>
        </div>

        <div className="lane-grid">
          {workflowLanes.map((lane, index) => (
            <Reveal key={lane.lane} delay={index * 90} className="lane-card">
              <span className="lane-card__index">0{index + 1}</span>
              <p className="lane-card__eyebrow">{lane.lane}</p>
              <h3>{lane.owner}</h3>
              <p>{lane.output}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
