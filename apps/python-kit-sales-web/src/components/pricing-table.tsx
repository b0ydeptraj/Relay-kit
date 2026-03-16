import Link from "next/link";
import { Reveal } from "@/components/reveal";
import { comparisonRows, pricingTiers } from "@/content/site";

interface PricingTableProps {
  variant?: "preview" | "full";
}

function PlanCard({
  tier,
  delay = 0,
  compact = false,
}: {
  tier: (typeof pricingTiers)[number];
  delay?: number;
  compact?: boolean;
}) {
  return (
    <Reveal delay={delay} className={`pricing-plan${tier.recommended ? " pricing-plan--featured" : ""}${compact ? " pricing-plan--compact" : ""}`}>
      <div className="pricing-plan__top">
        <div>
          <span className="pricing-plan__tag">{tier.billingModel}</span>
          <h3>{tier.name}</h3>
        </div>
        {tier.recommended ? <span className="pricing-plan__flag">Recommended</span> : null}
      </div>

      <div className="pricing-plan__price">
        <strong>{tier.price}</strong>
        <span>{tier.cadence}</span>
      </div>

      <p className="pricing-plan__tagline">{tier.tagline}</p>
      <p className="pricing-plan__anchor">{tier.anchor}</p>

      <div className="pricing-plan__block">
        <span>Included</span>
        <ul>
          {tier.deliverables.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="pricing-plan__block">
        <span>Best for</span>
        <ul>
          {tier.fit.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <Link href={`/checkout?plan=${tier.slug}`} className={`button ${tier.recommended ? "button--light" : "button--dark"}`}>
        {tier.cta}
      </Link>
    </Reveal>
  );
}

export function PricingTable({ variant = "preview" }: PricingTableProps) {
  if (variant === "preview") {
    return (
      <div className="pricing-preview">
        <div className="pricing-preview__grid">
          {pricingTiers.map((tier, index) => (
            <PlanCard key={tier.slug} tier={tier} delay={index * 80} compact />
          ))}
        </div>
        <div className="pricing-preview__foot">
          <p>
            Start with adoption depth, not a fake enterprise ladder. The continuity plan only exists once the
            workflow is already real.
          </p>
          <Link href="/pricing" className="button button--secondary button--small">
            Open full pricing
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="pricing-stack">
      <section className="pricing-steps">
        {[
          {
            step: "Step 1",
            title: "Choose the adoption depth.",
            body: "Solo Builder is for one operator. Team Workflow is for a team standardizing delivery behavior.",
          },
          {
            step: "Step 2",
            title: "Run it as policy, not as a toy purchase.",
            body: "Lane state, proof gates, and adapter parity matter only if the team actually operates against them.",
          },
          {
            step: "Step 3",
            title: "Add continuity when the baseline becomes infrastructure.",
            body: "Operator Continuity is not a starter plan. It exists for maintainers who want release rhythm after adoption.",
          },
        ].map((item, index) => (
          <Reveal key={item.step} delay={index * 80} className="pricing-step">
            <span>{item.step}</span>
            <h3>{item.title}</h3>
            <p>{item.body}</p>
          </Reveal>
        ))}
      </section>

      <section className="pricing-board-v2">
        <div className="pricing-board-v2__header">
          <div>
            <p className="eyebrow">Offer stack</p>
            <h2>Three plans. Three jobs. No fake enterprise sprawl.</h2>
            <p>
              Read the cards as operational entry points: one for a solo operator, one for a delivery team,
              one for long-lived stewardship.
            </p>
          </div>
        </div>

        <div className="pricing-board-v2__grid">
          {pricingTiers.map((tier, index) => (
            <PlanCard key={tier.slug} tier={tier} delay={index * 100} />
          ))}
        </div>
      </section>

      <section className="pricing-guidance">
        <div className="pricing-guidance__lead">
          <p className="eyebrow">Decision guide</p>
          <h2>If you only need one answer, start here.</h2>
          <p>
            Most teams should not overbuy. Choose the plan that matches the amount of operating change your team can actually absorb now.
          </p>
        </div>

        <div className="pricing-guidance__grid">
          {pricingTiers.map((tier, index) => (
            <Reveal key={`${tier.slug}-decision`} delay={index * 80} className="pricing-guidance__item">
              <span>{tier.name}</span>
              <h3>{tier.anchor}</h3>
              <p>{tier.fit[0]}</p>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="pricing-matrix">
        <div className="pricing-matrix__header">
          <p className="eyebrow">Capability matrix</p>
          <h2>Compare the commercial surface without losing the operational story.</h2>
          <p>
            The matrix answers practical buying questions after the higher-level adoption decision is already clear.
          </p>
        </div>

        <div className="comparison-table comparison-table--dark">
          <table>
            <thead>
              <tr>
                <th>Capability</th>
                <th>Solo Builder</th>
                <th>Team Workflow</th>
                <th>Operator Continuity</th>
              </tr>
            </thead>
            <tbody>
              {comparisonRows.map((row) => (
                <tr key={row.label}>
                  <td>{row.label}</td>
                  <td>{row.solo}</td>
                  <td>{row.team}</td>
                  <td>{row.continuity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="pricing-band">
        <div>
          <p className="eyebrow">Next move</p>
          <h2>Buy the baseline you can operationalize now, not the one that sounds biggest.</h2>
        </div>
        <Link href="/checkout?plan=team-workflow" className="button button--primary">
          Continue to checkout
        </Link>
      </section>
    </div>
  );
}
