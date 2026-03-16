import Link from "next/link";
import { BrandMark } from "@/components/brand-mark";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="shell site-footer__inner">
        <div className="site-footer__intro">
          <BrandMark compact />
          <p className="site-footer__copy">
            Relay-kit sells the operating model, not a prompt pack: promoted baselines, parity checks,
            durable state, QA gates, and evidence that survives real work.
          </p>
        </div>

        <div className="site-footer__column">
          <p className="site-footer__heading">Proof surface</p>
          <ul className="site-footer__list">
            <li>`baseline` is the official active bundle</li>
            <li>`.claude`, `.agent`, and `.codex` stay parity-checked</li>
            <li>gauntlet-backed discipline utilities are already promoted</li>
          </ul>
        </div>

        <div className="site-footer__column">
          <p className="site-footer__heading">Jump</p>
          <div className="site-footer__links">
            <Link href="/#commands">Commands</Link>
            <Link href="/pricing">Pricing</Link>
            <Link href="/checkout?plan=team-workflow">Checkout</Link>
            <a href="https://github.com/b0ydeptraj/ai-kit" target="_blank" rel="noreferrer">
              Repository
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
