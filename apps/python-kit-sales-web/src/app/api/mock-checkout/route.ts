import { NextResponse } from "next/server";
import { createCheckoutResponse, normalizePayload } from "@/lib/checkout";

export async function POST(request: Request) {
  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ errors: { form: "Request body must be JSON." } }, { status: 400 });
  }

  const normalized = normalizePayload(body);
  if (!normalized.ok) {
    return NextResponse.json({ errors: normalized.errors }, { status: 422 });
  }

  return NextResponse.json(createCheckoutResponse(normalized.data), { status: 200 });
}
