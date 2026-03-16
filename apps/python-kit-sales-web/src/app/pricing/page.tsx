import { Reveal } from "@/components/reveal";
import { PricingTable } from "@/components/pricing-table";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { faqItems, pricingSignals, surfaceCounts } from "@/content/site";

export default function PricingPage() {
  return (
    <div className="page-shell">
      <SiteHeader />
      <main className="page-main">
        <section className="page-hero">
          <div className="shell page-hero__grid">
            <div className="page-hero__body">
              <p className="eyebrow">Pricing</p>
              <h1>Choose the adoption shape your team can actually operationalize.</h1>
              <p>
                Start with a one-time baseline, expand into team behavior when the delivery model becomes shared,
                and pay for continuity only when the workflow turns into operating infrastructure.
              </p>
            </div>

            <div className="page-hero__stack">
              {pricingSignals.map((signal, index) => (
                <Reveal key={signal.label} delay={index * 80} className="page-hero__card">
                  <span>{signal.label}</span>
                  <h2>{signal.title}</h2>
                  <p>{signal.body}</p>
                </Reveal>
              ))}
            </div>
          </div>

          <div className="shell">
            <div className="surface-count-grid surface-count-grid--tight">
              {surfaceCounts.map((item, index) => (
                <Reveal key={item.label} delay={index * 70} className="surface-count-card surface-count-card--light">
                  <strong>{item.value}</strong>
                  <span>{item.label}</span>
                  <p>{item.note}</p>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <div className="dark-stage">
          <section className="section section--dark">
            <div className="shell">
              <PricingTable variant="full" />
            </div>
          </section>

          <section className="section section--dark">
            <div className="shell">
              <div className="section-head section-head--dark section-head--wide">
                <p className="eyebrow">FAQ</p>
                <h2>Commercial edges, answered the way a builder would ask them.</h2>
                <p>
                  Keep the tone direct. This page sells a technical operating system, not a generic marketing wrapper.
                </p>
              </div>

              <div className="faq-grid faq-grid--dark">
                {faqItems.map((item, index) => (
                  <Reveal key={item.question} delay={index * 60} className="faq-card-v2">
                    <h3>{item.question}</h3>
                    <p>{item.answer}</p>
                  </Reveal>
                ))}
              </div>
            </div>
          </section>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
