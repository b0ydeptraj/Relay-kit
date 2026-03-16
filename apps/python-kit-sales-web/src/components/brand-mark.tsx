import Link from "next/link";

interface BrandMarkProps {
  href?: string;
  compact?: boolean;
}

export function BrandMark({ href = "/", compact = false }: BrandMarkProps) {
  return (
    <Link href={href} className={`brand-lockup${compact ? " brand-lockup--compact" : ""}`} aria-label="Relay-kit home">
      <span className="brand-lockup__glyph" aria-hidden="true">
        <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="2" width="44" height="44" rx="14" fill="#1D1724" />
          <path d="M14 34V14H22.5C27 14 30 16.7 30 21C30 25.3 27 28 22.5 28H14" stroke="#F7EFE5" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M30.5 14V34" stroke="#C86F48" strokeWidth="3.5" strokeLinecap="round" />
          <path d="M30.5 24L38 15.5" stroke="#8CD1C1" strokeWidth="3.5" strokeLinecap="round" />
          <path d="M30.5 24L38 34" stroke="#8CD1C1" strokeWidth="3.5" strokeLinecap="round" />
        </svg>
      </span>

      <span className="brand-lockup__text">
        <span className="brand-lockup__eyebrow">proof-first workflow OS</span>
        <span className="brand-lockup__wordmark">
          <span className="brand-lockup__wordmark-main">Relay</span>
          <span className="brand-lockup__wordmark-accent">-kit</span>
        </span>
      </span>
    </Link>
  );
}
