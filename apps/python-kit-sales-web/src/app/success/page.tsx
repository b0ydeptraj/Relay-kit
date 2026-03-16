import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getRecommendedTier, getTierBySlug } from "@/content/site";
import { isTierSlug } from "@/lib/checkout";

type SuccessPageProps = {
  searchParams?: Promise<{ orderId?: string; plan?: string }>;
};

export default async function SuccessPage({ searchParams }: SuccessPageProps) {
  const params = (await searchParams) ?? {};
  const fallback = getRecommendedTier();
  const tier = params.plan && isTierSlug(params.plan) ? getTierBySlug(params.plan) ?? fallback : fallback;
  const orderId = params.orderId?.trim() || "RK-DEMO-MISSING";

  return (
    <div className="page-shell">
      <SiteHeader />
      <main className="page-main">
        <section className="page-hero">
          <div className="shell page-hero__grid">
            <div className="page-hero__body">
              <p className="eyebrow">Confirmation</p>
              <h1>The purchase is fake. The evidence chain is real.</h1>
              <p>
                Plan <strong>{tier.name}</strong> is now attached to confirmation <strong>{orderId}</strong>. The page proves a real multi-step
                flow without pretending payment, auth, or subscriptions already exist.
              </p>
            </div>
          </div>
        </section>

        <div className="dark-stage">
          <section className="section section--dark">
            <div className="shell success-grid-v2">
              <article className="success-panel-v2 success-panel-v2--paper">
                <p className="eyebrow">Suggested next command</p>
                <h2>Generate the active baseline into the next workspace.</h2>
                <p>
                  The sales story should always resolve into a concrete operating move, not a vague thank-you page.
                </p>
                <div className="success-command-v2">
                  <code>python python_kit.py . --bundle baseline --ai all --emit-contracts --emit-docs --emit-reference-templates</code>
                </div>
              </article>

              <aside className="success-panel-v2 success-panel-v2--night">
                <p className="eyebrow">Next step</p>
                <h3>{tier.name} summary</h3>
                <ul>
                  {tier.deliverables.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
                <div className="form-actions">
                  <Link href="/" className="button button--secondary">
                    Back to landing
                  </Link>
                  <Link href="/pricing" className="button button--primary">
                    Review plans
                  </Link>
                </div>
              </aside>
            </div>
          </section>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
