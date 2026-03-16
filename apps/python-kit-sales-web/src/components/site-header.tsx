import Link from "next/link";
import { BrandMark } from "@/components/brand-mark";

const navItems = [
  { href: "/#commands", label: "Commands" },
  { href: "/#system", label: "System" },
  { href: "/#proof", label: "Proof" },
  { href: "/pricing", label: "Pricing" },
] as const;

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="shell site-header__inner">
        <div className="site-header__brand">
          <BrandMark compact />
          <span className="site-header__status">baseline live</span>
        </div>

        <nav className="site-nav" aria-label="Primary navigation">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="site-nav__link">
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="site-header__actions">
          <Link href="/checkout?plan=team-workflow" className="button button--primary button--small">
            Adopt the baseline
          </Link>
        </div>
      </div>
    </header>
  );
}
