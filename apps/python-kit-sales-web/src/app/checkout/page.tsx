import { CheckoutForm } from "@/components/checkout-form";
import { Reveal } from "@/components/reveal";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getRecommendedTier, getTierBySlug } from "@/content/site";
import { isTierSlug } from "@/lib/checkout";

type CheckoutPageProps = {
  searchParams?: Promise<{ plan?: string }>;
};

export default async function CheckoutPage({ searchParams }: CheckoutPageProps) {
  const params = (await searchParams) ?? {};
  const fallback = getRecommendedTier();
  const tier = params.plan && isTierSlug(params.plan) ? getTierBySlug(params.plan) ?? fallback : fallback;

  return (
    <div className="page-shell">
      <SiteHeader />
      <main className="page-main">
        <section className="page-hero">
          <div className="shell page-hero__grid">
            <div className="page-hero__body">
              <p className="eyebrow">Checkout</p>
              <h1>Make the fake purchase feel as credible as the product story.</h1>
              <p>
                This is not production billing. It is a proof-driven checkout: query-selected plan, form state,
                validation, API handling, and confirmation flow that behaves like a real internal purchase request.
              </p>
            </div>

            <Reveal className="page-hero__card page-hero__card--selected">
              <span>Selected tier</span>
              <h2>{tier.name}</h2>
              <p>{tier.anchor}</p>
            </Reveal>
          </div>
        </section>

        <div className="dark-stage">
          <section className="section section--dark">
            <div className="shell">
              <CheckoutForm initialPlan={tier.slug} />
            </div>
          </section>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
