#!/usr/bin/env python3
"""
content_spinner.py - Content variation engine for MMO/social media automation.
Spins text with synonyms, sentence restructuring, and emoji variation.
Also generates AI-prompted content variations via OpenAI/Gemini API.

Usage:
    python scripts/content_spinner.py --input template.txt --count 20 --output variants.txt
    python scripts/content_spinner.py --text "Check out my new post!" --count 10
    python scripts/content_spinner.py --input template.txt --ai --api-key KEY
    python scripts/content_spinner.py --generate-captions --niche fashion --count 15
"""
import argparse
import json
import os
import random
import re
import sys
import time

# Synonym banks for spinning
SYNONYMS = {
    "amazing": ["awesome", "incredible", "fantastic", "brilliant", "stunning", "remarkable"],
    "great": ["excellent", "wonderful", "superb", "outstanding", "terrific", "magnificent"],
    "good": ["nice", "solid", "quality", "decent", "fine", "splendid"],
    "buy": ["grab", "get", "purchase", "pick up", "snag", "order"],
    "check": ["look at", "see", "view", "explore", "discover", "browse"],
    "post": ["content", "update", "share", "pic", "photo", "upload"],
    "love": ["adore", "obsessed with", "living for", "can't get enough of", "absolutely love"],
    "new": ["fresh", "latest", "brand new", "just dropped", "newly released"],
    "sale": ["deal", "offer", "discount", "promo", "special", "savings"],
    "follow": ["subscribe", "join", "connect", "stay tuned"],
    "link": ["URL", "page", "shop", "store"],
    "today": ["now", "right now", "this moment", "currently", "at this time"],
    "beautiful": ["stunning", "gorgeous", "breathtaking", "lovely", "elegant", "pretty"],
    "happy": ["excited", "thrilled", "delighted", "stoked", "pumped", "ecstatic"],
}

EMOJI_SETS = {
    "positive": ["🔥", "💯", "✨", "⭐", "🌟", "💪", "🎉", "🙌", "👏", "❤️", "💕", "🥰"],
    "shopping": ["🛍️", "💳", "🏷️", "🎁", "🛒", "💰", "💸", "✅", "📦", "🚚"],
    "food": ["🍔", "🍕", "🍜", "🌮", "🍣", "☕", "🧁", "🍰", "🥗", "😋"],
    "fashion": ["👗", "👠", "👜", "💄", "💅", "👑", "✨", "🌸", "💃", "🪞"],
    "fitness": ["💪", "🏋️", "🏃", "🥗", "💦", "🏆", "⚡", "🔥", "🧘", "🏅"],
    "tech": ["💻", "📱", "⚡", "🚀", "🤖", "🔧", "💡", "🌐", "📡", "🎮"],
    "travel": ["✈️", "🌍", "🗺️", "🏖️", "🏔️", "🌅", "🧳", "📸", "🗼", "🌴"],
    "general": ["🔥", "✨", "💯", "❤️", "👉", "⬇️", "👇", "✅", "📌", "💡"],
}

CAPTION_TEMPLATES = {
    "fashion": [
        "Obsessed with this {adj} look! 😍 {cta}",
        "New {item} just dropped and I'm LIVING for it ✨ {cta}",
        "When your outfit is on point 💅 Shop the look {cta}",
        "Style inspo for your {day} 🌸 {cta}",
    ],
    "food": [
        "This {adj} {dish} is absolutely INCREDIBLE 😋 Recipe {cta}",
        "Foodie heaven 🍴 Can't stop thinking about this {dish}",
        "Cooking up something {adj} today! Full recipe {cta}",
        "Weekend meals hitting different 🔥 {cta}",
    ],
    "fitness": [
        "Day {n} of my {adj} fitness journey 💪 {cta}",
        "No excuses! Here's my {adj} workout routine 🔥 {cta}",
        "Results don't lie 📈 {adj} progress after {n} weeks! {cta}",
        "Gym aesthetic ✨ {cta}",
    ],
    "general": [
        "{emoji} {adj} content incoming! {cta}",
        "You don't want to miss this {adj} update! {cta}",
        "Dropping something {adj} today 🚀 {cta}",
        "This is why everyone's talking about it {emoji} {cta}",
    ],
}

CTA_VARIANTS = [
    "Link in bio! 👆", "Tap the link! 👇", "Shop now →", "Click link in bio ⬆️",
    "DM for info!", "Comment below! 💬", "Save this post! 🔖", "Share with friends! 📲",
    "Follow for more! ✅", "Turn on notifications! 🔔", "Link in bio for details!",
]

FILLERS = {
    "adj": ["amazing", "incredible", "stunning", "gorgeous", "epic", "game-changing", "must-have"],
    "day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
            "weekday", "weekend"],
    "n": [str(i) for i in range(1, 31)],
    "item": ["dress", "outfit", "look", "collection", "piece", "style"],
    "dish": ["pasta", "salad", "bowl", "recipe", "meal", "creation"],
    "emoji": EMOJI_SETS["general"],
}


def spin_text(text: str, spin_count: int = 1) -> list:
    """Generate variations of text by replacing words with synonyms."""
    results = set()
    attempts = 0
    while len(results) < spin_count and attempts < spin_count * 5:
        attempts += 1
        variant = text
        # Replace synonyms
        for word, syns in SYNONYMS.items():
            if re.search(rf'\b{word}\b', variant, re.IGNORECASE):
                replacement = random.choice(syns)
                variant = re.sub(rf'\b{word}\b', replacement, variant, count=1, flags=re.IGNORECASE)
        # Add random emoji
        if random.random() > 0.5:
            emoji = random.choice(EMOJI_SETS["general"])
            variant = variant.rstrip() + f" {emoji}"
        if variant != text:
            results.add(variant)
    return list(results)[:spin_count]


def generate_captions(niche: str, count: int) -> list:
    templates = CAPTION_TEMPLATES.get(niche, CAPTION_TEMPLATES["general"])
    results = []
    for _ in range(count):
        tmpl = random.choice(templates)
        filled = tmpl
        for key, options in FILLERS.items():
            if f"{{{key}}}" in filled:
                filled = filled.replace(f"{{{key}}}", random.choice(options))
        filled = filled.replace("{cta}", random.choice(CTA_VARIANTS))
        # Add hashtags
        hashtag_count = random.randint(3, 10)
        niche_tags = {
            "fashion": ["#fashion","#style","#ootd","#outfit","#trendy","#fashionista","#clothing"],
            "food": ["#food","#foodie","#recipe","#cooking","#delicious","#homemade","#yummy"],
            "fitness": ["#fitness","#gym","#workout","#health","#fit","#motivation","#exercise"],
            "general": ["#viral","#trending","#fyp","#foryou","#explore","#content","#daily"],
        }
        tags = random.sample(niche_tags.get(niche, niche_tags["general"]), min(hashtag_count, len(niche_tags.get(niche, niche_tags["general"]))))
        filled += "\n\n" + " ".join(tags)
        results.append(filled)
    return results


def ai_spin(texts: list, api_key: str, count_per_text: int = 3) -> list:
    """Use OpenAI GPT to generate variations."""
    try:
        import urllib.request as ureq
        results = []
        for text in texts:
            payload = json.dumps({
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": f"Rewrite the following text {count_per_text} different ways, keeping the same meaning but varying the wording. Output as JSON array:\n\n{text}"}],
                "max_tokens": 500,
            }).encode()
            req = ureq.Request("https://api.openai.com/v1/chat/completions", payload,
                               {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
            resp = ureq.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            try:
                variants = json.loads(content)
                results.extend(variants)
            except:
                results.append(content)
            time.sleep(0.5)
        return results
    except Exception as e:
        print(f"[-] AI spin failed: {e}")
        return []


def main():
    p = argparse.ArgumentParser(description="Content spinner and caption generator")
    p.add_argument("--text", help="Text to spin")
    p.add_argument("--input", help="Input template file (.txt)")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--output", help="Output file (.txt)")
    p.add_argument("--generate-captions", action="store_true")
    p.add_argument("--niche", choices=["fashion","food","fitness","general"], default="general")
    p.add_argument("--ai", action="store_true", help="Use AI to spin (requires --api-key)")
    p.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY",""))
    args = p.parse_args()

    results = []
    if args.generate_captions:
        results = generate_captions(args.niche, args.count)
        print(f"[+] Generated {len(results)} {args.niche} captions:")
    elif args.ai and args.api_key:
        texts = []
        if args.text: texts = [args.text]
        elif args.input:
            with open(args.input) as f:
                texts = [l.strip() for l in f if l.strip()]
        results = ai_spin(texts, args.api_key, args.count)
        print(f"[+] AI generated {len(results)} variants")
    else:
        text = args.text
        if args.input:
            with open(args.input) as f:
                text = f.read().strip()
        if not text:
            print("[-] --text, --input, or --generate-captions required"); sys.exit(1)
        results = spin_text(text, args.count)
        if not results:
            results = [text] * min(args.count, 3)
            print("[!] No synonyms found - text returned unchanged")
        print(f"[+] Spun {len(results)} variants:")

    for i, r in enumerate(results[:5]):
        print(f"\n[{i+1}] {r[:120]}...")

    if len(results) > 5:
        print(f"\n... and {len(results)-5} more")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n---\n".join(results))
        print(f"\n[+] Saved to {args.output}")


if __name__ == "__main__":
    main()
