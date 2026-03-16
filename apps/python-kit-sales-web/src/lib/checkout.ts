import { getTierBySlug, pricingTiers, type TierSlug } from "@/content/site";

export interface CheckoutPayload {
  plan: TierSlug;
  name: string;
  email: string;
  team: string;
  useCase: string;
}

export interface CheckoutResponse {
  orderId: string;
  plan: TierSlug;
  tierName: string;
  billingModel: string;
}

export type CheckoutErrors = Partial<Record<keyof CheckoutPayload, string>> & {
  form?: string;
};

export function isTierSlug(value: string): value is TierSlug {
  return pricingTiers.some((tier) => tier.slug === value);
}

export function validateCheckoutPayload(payload: Partial<CheckoutPayload>): CheckoutErrors {
  const errors: CheckoutErrors = {};

  if (!payload.plan || !isTierSlug(payload.plan)) {
    errors.plan = "Select a valid plan.";
  }

  if (!payload.name?.trim()) {
    errors.name = "Name is required.";
  }

  const email = payload.email?.trim() ?? "";
  if (!email) {
    errors.email = "Email is required.";
  } else if (!email.includes("@") || email.startsWith("@") || email.endsWith("@")) {
    errors.email = "Enter a valid email address.";
  }

  if (!payload.team?.trim()) {
    errors.team = "Team or company name is required.";
  }

  if (!payload.useCase?.trim()) {
    errors.useCase = "Tell us what you want Relay-kit to improve.";
  }

  return errors;
}

export function createMockOrderId(plan: TierSlug): string {
  const stamp = Date.now().toString(36).toUpperCase();
  const label = plan.replace(/-/g, "").slice(0, 6).toUpperCase();
  return `RK-${label}-${stamp}`;
}

export function normalizePayload(input: unknown):
  | { ok: true; data: CheckoutPayload }
  | { ok: false; errors: CheckoutErrors } {
  if (!input || typeof input !== "object") {
    return { ok: false, errors: { form: "Invalid request body." } };
  }

  const record = input as Record<string, unknown>;
  const payload: Partial<CheckoutPayload> = {
    plan: typeof record.plan === "string" ? (record.plan as TierSlug) : undefined,
    name: typeof record.name === "string" ? record.name : "",
    email: typeof record.email === "string" ? record.email : "",
    team: typeof record.team === "string" ? record.team : "",
    useCase: typeof record.useCase === "string" ? record.useCase : "",
  };

  const errors = validateCheckoutPayload(payload);
  if (Object.keys(errors).length > 0) {
    return { ok: false, errors };
  }

  return { ok: true, data: payload as CheckoutPayload };
}

export function createCheckoutResponse(payload: CheckoutPayload): CheckoutResponse {
  const tier = getTierBySlug(payload.plan);
  if (!tier) {
    throw new Error("Unknown tier.");
  }

  return {
    orderId: createMockOrderId(payload.plan),
    plan: payload.plan,
    tierName: tier.name,
    billingModel: tier.billingModel,
  };
}
