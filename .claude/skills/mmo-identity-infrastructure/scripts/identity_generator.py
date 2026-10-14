#!/usr/bin/env python3
"""
identity_generator.py - Generate realistic fake identities for MMO account creation.
Produces consistent persona: name, DOB, email, phone, address, username combos.

Usage:
    python scripts/identity_generator.py --count 10 --nationality vn --output identities.json
    python scripts/identity_generator.py --count 5 --nationality us --format csv
    python scripts/identity_generator.py --count 1 --nationality uk --verbose
"""
import argparse
import csv
import json
import os
import random
import string
import sys
import time

# Name data banks
NAMES = {
    "vn": {
        "first_m": ["Minh","Hùng","Tuấn","Đức","Dũng","Hải","Nam","Bình","Thành","Long","Phong","Hiếu","Quân","Trí"],
        "first_f": ["Lan","Hoa","Hương","Mai","Linh","Thảo","Ngọc","Phương","Anh","Trang","Thủy","Yến","Diệp"],
        "last":    ["Nguyễn","Trần","Lê","Phạm","Hoàng","Huỳnh","Phan","Vũ","Đặng","Bùi","Đỗ","Hồ","Ngô","Dương"],
        "email_providers": ["gmail.com","yahoo.com","outlook.com","hotmail.com"],
        "phone_prefix": ["03","07","08","09"],
        "country_code": "+84","country": "Vietnam",
        "tlds": [".vn",".com"],
    },
    "us": {
        "first_m": ["James","John","Robert","Michael","William","David","Richard","Thomas","Charles","Daniel"],
        "first_f": ["Mary","Patricia","Jennifer","Linda","Barbara","Elizabeth","Susan","Jessica","Sarah","Karen"],
        "last":    ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Martinez","Wilson"],
        "email_providers": ["gmail.com","yahoo.com","outlook.com","hotmail.com","icloud.com"],
        "phone_prefix": ["201","212","310","415","512","617","702","718","213","404"],
        "country_code": "+1","country": "United States",
        "tlds": [".com",".net"],
    },
    "uk": {
        "first_m": ["Oliver","Jack","Harry","George","Charlie","Jacob","Alfie","Freddie","Oscar","Archie"],
        "first_f": ["Olivia","Amelia","Isla","Ava","Emily","Isabella","Mia","Poppy","Ella","Grace"],
        "last":    ["Smith","Jones","Taylor","Brown","Williams","Wilson","Johnson","Davies","Robinson","Evans"],
        "email_providers": ["gmail.com","yahoo.co.uk","hotmail.co.uk","outlook.com","protonmail.com"],
        "phone_prefix": ["07700","07711","07722","07733","07800","07900"],
        "country_code": "+44","country": "United Kingdom",
        "tlds": [".co.uk",".com"],
    },
    "de": {
        "first_m": ["Lars","Finn","Leon","Jonas","Julian","Felix","Niklas","Moritz","Max","Paul"],
        "first_f": ["Emma","Hannah","Mia","Sophia","Lena","Anna","Lisa","Laura","Sarah","Katharina"],
        "last":    ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Schulz","Hoffmann"],
        "email_providers": ["gmail.com","web.de","gmx.de","t-online.de","outlook.de"],
        "phone_prefix": ["015","016","017"],
        "country_code": "+49","country": "Germany",
        "tlds": [".de",".com"],
    },
}

USERNAME_STYLES = ["first.last","first_last","flast","firstXXX","lastfirstXX","randomXXXX"]


def random_dob(min_age: int = 18, max_age: int = 45) -> dict:
    year = random.randint(2024 - max_age, 2024 - min_age)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return {"year": year, "month": month, "day": day,
            "dob": f"{year}-{month:02d}-{day:02d}",
            "age": 2024 - year}


def generate_username(first: str, last: str) -> str:
    style = random.choice(USERNAME_STYLES)
    n = random.randint(10, 99)
    nn = random.randint(100, 999)
    f = first.lower().replace(" ", "").replace("ă","a").replace("â","a").replace("ê","e").replace("ô","o").replace("ơ","o").replace("ư","u").replace("đ","d")
    l = last.lower().replace(" ", "").replace("ă","a").replace("â","a").replace("ê","e").replace("ô","o").replace("ơ","o").replace("ư","u").replace("đ","d")
    # Remove diacritics roughly
    for ch in "àáảãạăắặẵẳầấậẫẩèéẹẻẽêềếệễểìíịỉĩòóọỏõôồốộỗổơờớợỡởùúụủũưừứựữửỳýỵỷỹđ":
        plain = "aaaaaaaaaaaaaaaaaaeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyy d"
        idx = "àáảãạăắặẵẳầấậẫẩèéẹẻẽêềếệễểìíịỉĩòóọỏõôồốộỗổơờớợỡởùúụủũưừứựữửỳýỵỷỹđ".find(ch)
        if idx >= 0 and idx < len(plain):
            f = f.replace(ch, plain[idx])
            l = l.replace(ch, plain[idx])
    styles = {
        "first.last": f"{f}.{l}", "first_last": f"{f}_{l}",
        "flast": f"{f[0]}{l}", "firstXXX": f"{f}{nn}",
        "lastfirstXX": f"{l}{f[0]}{n}", "randomXXXX": f"{f}{random.randint(1000,9999)}",
    }
    return styles.get(style, f"{f}{n}")


def generate_email(first: str, last: str, provider: str, nationality: str) -> str:
    username = generate_username(first, last)
    sep = random.choice([".", "_", ""])
    n = random.randint(0, 99)
    variants = [
        f"{username}@{provider}",
        f"{username}{n}@{provider}",
        f"{first.lower()[:3]}{last.lower()[:4]}{n}@{provider}",
    ]
    return random.choice(variants)


def generate_phone(nationality: str, data: dict) -> str:
    prefix = random.choice(data["phone_prefix"])
    suffix_len = 7 if nationality in ["us","uk"] else (7 if prefix.startswith("0") else 7)
    suffix = "".join([str(random.randint(0, 9)) for _ in range(suffix_len)])
    return f"{data['country_code']} {prefix}{suffix}"


def generate_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(random.choices(chars, k=length))


def generate_identity(nationality: str = "us", gender: str = None) -> dict:
    data = NAMES.get(nationality, NAMES["us"])
    gender = gender or random.choice(["m", "f"])
    first = random.choice(data["first_m"] if gender == "m" else data["first_f"])
    last  = random.choice(data["last"])
    dob   = random_dob()
    provider = random.choice(data["email_providers"])
    email    = generate_email(first, last, provider, nationality)
    phone    = generate_phone(nationality, data)
    username = generate_username(first, last)
    password = generate_password()

    return {
        "first_name": first, "last_name": last,
        "full_name": f"{first} {last}" if nationality != "vn" else f"{last} {first}",
        "gender": "male" if gender == "m" else "female",
        "dob": dob["dob"], "age": dob["age"],
        "email": email, "email_password": password,
        "username": username, "account_password": generate_password(10),
        "phone": phone, "country": data["country"],
        "nationality": nationality,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def main():
    p = argparse.ArgumentParser(description="Fake identity generator for MMO account ops")
    p.add_argument("--count", type=int, default=5)
    p.add_argument("--nationality", choices=list(NAMES.keys()), default="us")
    p.add_argument("--gender", choices=["m","f"], help="Force gender")
    p.add_argument("--output", help="Output JSON file")
    p.add_argument("--format", choices=["json","csv","table"], default="table")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    identities = [generate_identity(args.nationality, args.gender) for _ in range(args.count)]

    if args.format == "table" or args.verbose:
        print(f"\n{'Full Name':<25} {'Email':<40} {'Phone':<20} {'DOB':<12} {'Username':<20}")
        print("-" * 120)
        for ident in identities:
            print(f"{ident['full_name']:<25} {ident['email']:<40} {ident['phone']:<20} {ident['dob']:<12} {ident['username']:<20}")

    if args.format == "json" or args.output:
        output = args.output or "identities.json"
        with open(output, "w", encoding="utf-8") as f:
            json.dump(identities, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Saved {len(identities)} identities to {output}")

    if args.format == "csv":
        output = args.output or "identities.csv"
        with open(output, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=identities[0].keys())
            w.writeheader()
            w.writerows(identities)
        print(f"[+] Saved CSV: {output}")


if __name__ == "__main__":
    main()
