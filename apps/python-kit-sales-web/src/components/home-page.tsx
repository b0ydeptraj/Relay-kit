import Link from "next/link";
import { CommandPanel } from "@/components/command-panel";
import { PricingTable } from "@/components/pricing-table";
import { Reveal } from "@/components/reveal";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { WorkflowDiagram } from "@/components/workflow-diagram";
import {
  adapterCards,
  commandPanels,
  ctas,
  featureCards,
  heroStats,
  layerCards,
  proofClaims,
  surfaceCounts,
} from "@/content/site";

export function HomePage() {
  return (
    <div className="page-shell">
      <SiteHeader />
      <main className="page-main">
        <section className="hero-stage">
          <div className="shell hero-stage__grid">
            <div className="hero-copy">
              <p className="eyebrow">Workflow OS for AI builders</p>
              <h1 className="hero-copy__title">
                A baseline that looks deliberate on the surface and survives real delivery underneath.
              </h1>
              <p className="hero-copy__lead">
                Relay-kit is the layer between agent output and durable work: routing, contracts, state,
                debugging discipline, QA evidence, and parity checks that survive real implementation pressure.
              </p>

              <div className="hero-copy__actions">
                <Link href={ctas.primary} className="button button--primary">
                  Adopt the baseline
                </Link>
                <Link href={ctas.secondary} className="button button--secondary">
                  Inspect pricing
                </Link>
              </div>

              <div className="hero-stat-grid">
                {heroStats.map((stat) => (
                  <article key={stat.label} className="hero-stat">
                    <strong>{stat.value}</strong>
                    <span>{stat.label}</span>
                    <p>{stat.note}</p>
                  </article>
                ))}
              </div>
            </div>

            <aside className="hero-board" aria-label="brand promise">
              <div className="hero-board__lead">
                <p className="eyebrow">Brand promise</p>
                <h2>One polished front door. Three aligned runtimes. Proof at every handoff.</h2>
                <p>
                  The page should feel like a product with taste, not a generated marketing shell. The repo truth
                  still sits underneath it.
                </p>
              </div>

              <div className="hero-board__stack">
                {commandPanels.slice(0, 2).map((panel, index) => (
                  <CommandPanel key={panel.label} {...panel} variant="paper" compact delay={index * 120} />
                ))}
              </div>
            </aside>
          </div>
        </section>

        <section className="section section--light" id="commands">
          <div className="shell">
            <div className="section-head section-head--light">
              <p className="eyebrow">Surface counts</p>
              <h2>Show the repo surface in hard numbers, not just in claims.</h2>
              <p>
                The page should prove how much runtime surface exists now and what still survives only in the
                compatibility layer.
              </p>
            </div>

            <div className="surface-count-grid">
              {surfaceCounts.map((item, index) => (
                <Reveal key={item.label} delay={index * 70} className="surface-count-card">
                  <strong>{item.value}</strong>
                  <span>{item.label}</span>
                  <p>{item.note}</p>
                </Reveal>
              ))}
            </div>

            <div className="section-head section-head--light section-head--wide">
              <p className="eyebrow">Core routines</p>
              <h2>Show the commands people will actually remember.</h2>
              <p>
                The most convincing parts of Relay-kit are operational. Use command-style panels instead of burying
                the product inside generic marketing paragraphs.
              </p>
            </div>

            <div className="command-grid">
              {commandPanels.map((panel, index) => (
                <CommandPanel key={panel.label} {...panel} delay={index * 80} />
              ))}
            </div>
          </div>
        </section>

        <div className="dark-stage">
          <section className="section section--dark" id="system">
            <div className="shell system-layout">
              <div className="section-head section-head--dark section-head--transition">
                <p className="eyebrow">System architecture</p>
                <h2>Light on the outside. Disciplined underneath.</h2>
                <p>
                  The product story only works because the internal structure is explicit: route the work, run the
                  playbook, support the lane, then ship the artifact.
                </p>
              </div>

              <div className="layer-board">
                {layerCards.map((card, index) => (
                  <Reveal key={card.layer} delay={index * 90} className="layer-card">
                    <div className="layer-card__meta">
                      <span className="layer-card__label">{card.layer}</span>
                      <h3>{card.title}</h3>
                    </div>
                    <p>{card.body}</p>
                    <ul className="chip-list">
                      {card.outputs.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </Reveal>
                ))}
              </div>
            </div>
          </section>

          <section className="section section--dark" id="proof">
            <div className="shell proof-layout">
              <div className="proof-layout__lead">
                <div className="section-head section-head--dark">
                  <p className="eyebrow">Repo-backed proof</p>
                  <h2>The commercial story is only credible if the repo can prove it.</h2>
                  <p>
                    Active bundles, parity validation, gauntlet results, and `.ai-kit` artifacts are surfaced here as
                    product proof, not hidden internal trivia.
                  </p>
                </div>

                <div className="adapter-rack">
                  {adapterCards.map((card, index) => (
                    <Reveal key={card.name} delay={index * 90} className="adapter-card-v2">
                      <span>{card.surface}</span>
                      <h3>{card.name}</h3>
                      <p>{card.body}</p>
                    </Reveal>
                  ))}
                </div>
              </div>

              <div className="proof-layout__grid">
                {proofClaims.map((claim, index) => (
                  <Reveal key={claim.title} delay={index * 100} className="proof-card-v2">
                    <span className="proof-card-v2__signal">{claim.signal}</span>
                    <h3>{claim.title}</h3>
                    <p>{claim.body}</p>
                    <ul>
                      {claim.evidence.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </Reveal>
                ))}
              </div>
            </div>
          </section>

          <WorkflowDiagram />

          <section className="section section--dark">
            <div className="shell capability-layout-v2">
              <div className="section-head section-head--dark">
                <p className="eyebrow">Why teams buy</p>
                <h2>Better structure, better proof, less AI-looking output.</h2>
                <p>
                  The value is not one more prompt. The value is a system that makes product, build, and QA behave like
                  one delivery stack.
                </p>
              </div>

              <div className="feature-rack">
                {featureCards.map((card, index) => (
                  <Reveal key={card.title} delay={index * 75} className="feature-card-v2">
                    <span>{card.badge}</span>
                    <h3>{card.title}</h3>
                    <p>{card.body}</p>
                  </Reveal>
                ))}
              </div>
            </div>
          </section>

          <section className="section section--dark">
            <div className="shell">
              <div className="section-head section-head--dark section-head--wide">
                <p className="eyebrow">Pricing preview</p>
                <h2>Package the workflow like infrastructure, not like a generic template sale.</h2>
                <p>
                  Pricing should read like an operational decision: adopt the baseline, expand into team behavior, then
                  pay for continuity only when the workflow becomes part of the stack.
                </p>
              </div>
              <PricingTable variant="preview" />
            </div>
          </section>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
