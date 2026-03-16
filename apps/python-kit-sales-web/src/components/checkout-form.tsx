"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { getRecommendedTier, pricingTiers, type TierSlug } from "@/content/site";
import { validateCheckoutPayload, type CheckoutErrors, type CheckoutPayload } from "@/lib/checkout";

interface CheckoutFormProps {
  initialPlan?: TierSlug;
}

const defaultTier = getRecommendedTier();

export function CheckoutForm({ initialPlan }: CheckoutFormProps) {
  const router = useRouter();
  const [form, setForm] = useState<CheckoutPayload>({
    plan: initialPlan ?? defaultTier.slug,
    name: "",
    email: "",
    team: "",
    useCase: "",
  });
  const [errors, setErrors] = useState<CheckoutErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const selectedTier = useMemo(
    () => pricingTiers.find((tier) => tier.slug === form.plan) ?? defaultTier,
    [form.plan],
  );

  function updateField<K extends keyof CheckoutPayload>(key: K, value: CheckoutPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: undefined, form: undefined }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validation = validateCheckoutPayload(form);

    if (Object.keys(validation).length > 0) {
      setErrors(validation);
      return;
    }

    setSubmitting(true);
    setErrors({});

    try {
      const response = await fetch("/api/mock-checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const body = (await response.json()) as {
        orderId?: string;
        plan?: TierSlug;
        errors?: CheckoutErrors;
      };

      if (!response.ok || !body.orderId || !body.plan) {
        setErrors(body.errors ?? { form: "Checkout failed. Try again." });
        return;
      }

      router.push(`/success?plan=${body.plan}&orderId=${body.orderId}`);
    } catch {
      setErrors({ form: "Network error. This fake checkout still expects a working request." });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="checkout-stage">
      <section className="checkout-stage__main">
        <div className="checkout-stage__intro">
          <p className="eyebrow">Purchase flow</p>
          <h2>Review the operating tier, then send a believable internal purchase request.</h2>
          <p>
            The interaction should feel deliberate: strong plan state, clean form hierarchy, visible validation,
            and a summary rail that explains why this flow exists.
          </p>
        </div>

        <form className="checkout-stage__form" onSubmit={handleSubmit} noValidate>
          <section className="checkout-panel-v2 checkout-panel-v2--paper">
            <div className="checkout-panel-v2__head">
              <h3>Choose the operating tier</h3>
              <p>The plan choice should feel like an infrastructure decision, not like a marketing toy.</p>
            </div>

            <div className="plan-picker-grid" role="radiogroup" aria-label="Select plan">
              {pricingTiers.map((tier) => {
                const active = form.plan === tier.slug;
                return (
                  <label key={tier.slug} className={`tier-option${active ? " tier-option--active" : ""}`}>
                    <div className="tier-option__top">
                      <span className="tier-option__selection">
                        <input
                          type="radio"
                          name="plan"
                          checked={active}
                          onChange={() => updateField("plan", tier.slug)}
                        />
                        <strong>{tier.name}</strong>
                      </span>
                      <span className="tier-option__price">
                        {tier.price}
                        {tier.cadence !== "one-time" ? tier.cadence : ""}
                      </span>
                    </div>
                    <p>{tier.anchor}</p>
                    <div className="tier-option__meta">
                      <span>{tier.billingModel}</span>
                      {tier.recommended ? <strong>Recommended</strong> : null}
                    </div>
                  </label>
                );
              })}
            </div>
            {errors.plan ? <p className="field-error">{errors.plan}</p> : null}
          </section>

          <section className="checkout-panel-v2 checkout-panel-v2--paper">
            <div className="checkout-panel-v2__head">
              <h3>Buyer details</h3>
              <p>Minimal fields, but enough to read like a real internal request instead of a dead demo form.</p>
            </div>

            <div className="checkout-fields">
              <div className="field">
                <label htmlFor="name">Buyer name</label>
                <input
                  id="name"
                  className="input"
                  value={form.name}
                  onChange={(event) => updateField("name", event.target.value)}
                  placeholder="Minh Nguyen"
                />
                {errors.name ? <p className="field-error">{errors.name}</p> : null}
              </div>

              <div className="field-grid field-grid--two">
                <div className="field">
                  <label htmlFor="email">Work email</label>
                  <input
                    id="email"
                    className="input"
                    type="email"
                    value={form.email}
                    onChange={(event) => updateField("email", event.target.value)}
                    placeholder="builder@company.com"
                  />
                  {errors.email ? <p className="field-error">{errors.email}</p> : null}
                </div>

                <div className="field">
                  <label htmlFor="team">Team or company</label>
                  <input
                    id="team"
                    className="input"
                    value={form.team}
                    onChange={(event) => updateField("team", event.target.value)}
                    placeholder="Platform pod"
                  />
                  {errors.team ? <p className="field-error">{errors.team}</p> : null}
                </div>
              </div>

              <div className="field">
                <label htmlFor="useCase">Operational use case</label>
                <textarea
                  id="useCase"
                  className="textarea"
                  value={form.useCase}
                  onChange={(event) => updateField("useCase", event.target.value)}
                  placeholder="We need a baseline that survives handoffs, QA gates, and adapter drift."
                />
                {errors.useCase ? <p className="field-error">{errors.useCase}</p> : null}
              </div>
            </div>
          </section>

          {errors.form ? <p className="form-error">{errors.form}</p> : null}

          <div className="form-actions">
            <button className="button button--primary" type="submit" disabled={submitting}>
              {submitting ? "Submitting mock order..." : `Continue with ${selectedTier.name}`}
            </button>
            <Link href="/pricing" className="button button--secondary">
              Review pricing again
            </Link>
          </div>
        </form>
      </section>

      <aside className="checkout-stage__aside">
        <div className="checkout-summary-v2">
          <p className="eyebrow">Order summary</p>
          <h3>{selectedTier.name}</h3>
          <div className="checkout-summary-v2__price">
            <strong>{selectedTier.price}</strong>
            <span>{selectedTier.cadence}</span>
          </div>
          <p>{selectedTier.tagline}</p>

          <div className="checkout-summary-v2__block">
            <span>Included in this mock purchase</span>
            <ul>
              {selectedTier.deliverables.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="checkout-summary-v2__command">
            <span>Why this matters</span>
            <code>{"query-selected tier -> form validation -> API round-trip -> confirmation handoff"}</code>
          </div>
        </div>
      </aside>
    </div>
  );
}
