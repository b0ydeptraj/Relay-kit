#!/usr/bin/env python3
"""
telegram_bot_manager.py - Telegram Bot API automation manager.
Broadcast messages, manage channels, schedule posts, and handle member interactions.

Usage:
    python scripts/telegram_bot_manager.py --action send --chat @mychannel --message "Hello!"
    python scripts/telegram_bot_manager.py --action broadcast --chats chats.txt --message-file msg.txt
    python scripts/telegram_bot_manager.py --action schedule --chat @channel --message "Post!" --delay 3600
    python scripts/telegram_bot_manager.py --action forward --from @source --to @dest --count 10
    python scripts/telegram_bot_manager.py --action stats --chat @mychannel
    python scripts/telegram_bot_manager.py --action poll --chat @channel --question "Q?" --options "A,B,C"
    python scripts/telegram_bot_manager.py --action pin --chat @channel --message-id 123

BOT_TOKEN: TG_BOT_TOKEN env var or --token arg.
Get token: @BotFather on Telegram
"""
import argparse
import json
import os
import random
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
TG_API = "https://api.telegram.org/bot{token}/{method}"


def tg(method: str, data: dict = None, token: str = None) -> dict:
    """Call Telegram Bot API method."""
    t = token or BOT_TOKEN
    url = TG_API.format(token=t, method=method)
    if data:
        payload = json.dumps(data).encode()
        req = ureq.Request(url, payload, {"Content-Type": "application/json"})
    else:
        req = ureq.Request(url)
    try:
        resp = ureq.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"ok": False, "description": str(e)[:100]}


def send_message(chat_id: str, text: str, parse_mode: str = "HTML",
                 disable_preview: bool = False, reply_to: int = None,
                 token: str = None) -> dict:
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode,
            "disable_web_page_preview": disable_preview}
    if reply_to: data["reply_to_message_id"] = reply_to
    return tg("sendMessage", data, token)


def send_photo(chat_id: str, photo_url: str, caption: str = "",
               parse_mode: str = "HTML", token: str = None) -> dict:
    return tg("sendPhoto", {
        "chat_id": chat_id, "photo": photo_url,
        "caption": caption, "parse_mode": parse_mode
    }, token)


def send_poll(chat_id: str, question: str, options: list,
              is_anonymous: bool = True, token: str = None) -> dict:
    return tg("sendPoll", {
        "chat_id": chat_id, "question": question,
        "options": json.dumps(options), "is_anonymous": is_anonymous
    }, token)


def forward_messages(from_chat: str, to_chat: str,
                     message_ids: list, token: str = None) -> list:
    results = []
    for msg_id in message_ids:
        r = tg("forwardMessage", {
            "chat_id": to_chat, "from_chat_id": from_chat,
            "message_id": msg_id
        }, token)
        results.append(r)
        time.sleep(0.5)
    return results


def pin_message(chat_id: str, message_id: int, notify: bool = False, token: str = None) -> dict:
    return tg("pinChatMessage", {
        "chat_id": chat_id, "message_id": message_id,
        "disable_notification": not notify
    }, token)


def get_chat_stats(chat_id: str, token: str = None) -> dict:
    """Get basic chat info and member count."""
    chat = tg("getChat", {"chat_id": chat_id}, token)
    if not chat.get("ok"):
        return {"error": chat.get("description")}
    count = tg("getChatMemberCount", {"chat_id": chat_id}, token)
    chat_info = chat.get("result", {})
    member_count = count.get("result", 0)
    result = {
        "id": chat_info.get("id"),
        "title": chat_info.get("title"),
        "type": chat_info.get("type"),
        "username": chat_info.get("username"),
        "member_count": member_count,
        "description": chat_info.get("description","")[:100],
    }
    print(f"[*] Channel: {result['title']} (@{result['username']})")
    print(f"    Type: {result['type']} | Members: {member_count:,}")
    print(f"    Description: {result['description']}")
    return result


def get_recent_messages(chat_id: str, count: int = 10, token: str = None) -> list:
    """Get recent messages via getUpdates (only works for bot's own messages)."""
    r = tg("getUpdates", {"limit": min(count, 100), "offset": -count}, token)
    messages = []
    for update in r.get("result", []):
        msg = update.get("message") or update.get("channel_post")
        if msg and str(msg.get("chat",{}).get("id","")) == str(chat_id).lstrip("@"):
            messages.append(msg)
    return messages


def broadcast(chat_ids: list, text: str, delay: float = 1.0,
              photo_url: str = None, token: str = None) -> dict:
    """Broadcast message to multiple chats."""
    results = {"sent": 0, "failed": 0, "errors": []}
    total = len(chat_ids)
    for i, chat_id in enumerate(chat_ids):
        if photo_url:
            r = send_photo(chat_id, photo_url, text, token=token)
        else:
            r = send_message(chat_id, text, token=token)

        if r.get("ok"):
            results["sent"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({"chat": chat_id, "error": r.get("description","?")[:50]})
        print(f"  [{i+1}/{total}] {'OK' if r.get('ok') else 'FAIL'} | {chat_id}")

        # Rate limiting: TG allows 30 msg/s to different chats, 1/s same chat
        time.sleep(delay + random.uniform(0, delay * 0.3))

    print(f"\n[*] Broadcast: {results['sent']}/{total} sent | {results['failed']} failed")
    return results


def schedule_post(chat_id: str, text: str, delay_seconds: int,
                  photo_url: str = None, token: str = None):
    """Schedule a post after delay_seconds."""
    post_time = time.time() + delay_seconds
    print(f"[*] Scheduled post at {time.strftime('%H:%M:%S', time.localtime(post_time))} (in {delay_seconds}s)")
    time.sleep(delay_seconds)
    if photo_url:
        r = send_photo(chat_id, photo_url, text, token=token)
    else:
        r = send_message(chat_id, text, token=token)
    print(f"[{'OK' if r.get('ok') else 'FAIL'}] Scheduled post sent")
    return r


def get_me_bot(token: str = None) -> dict:
    r = tg("getMe", token=token)
    bot = r.get("result", {})
    print(f"[*] Bot: @{bot.get('username')} | {bot.get('first_name')} | id:{bot.get('id')}")
    return bot


def build_inline_keyboard(buttons: list) -> dict:
    """Build inline keyboard markup from list of [text, url/callback] pairs."""
    keyboard = []
    row = []
    for btn in buttons:
        if isinstance(btn, list):
            text, action = btn[0], btn[1]
        else:
            text, action = btn, btn
        if action.startswith("http"):
            row.append({"text": text, "url": action})
        else:
            row.append({"text": text, "callback_data": action})
        if len(row) >= 2:
            keyboard.append(row); row = []
    if row: keyboard.append(row)
    return {"inline_keyboard": keyboard}


def main():
    p = argparse.ArgumentParser(description="Telegram bot automation manager")
    p.add_argument("--token", default=os.environ.get("TG_BOT_TOKEN",""))
    p.add_argument("--action", choices=["send","broadcast","schedule","forward",
                                          "stats","poll","pin","me"], required=True)
    p.add_argument("--chat", help="Target chat ID or @username")
    p.add_argument("--chats", help="File with chat IDs (one per line)")
    p.add_argument("--message")
    p.add_argument("--message-file", help="Message text from file")
    p.add_argument("--photo-url", help="Photo URL to send")
    p.add_argument("--from-chat", help="Source for forward")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--delay", type=float, default=1.0)
    p.add_argument("--message-id", type=int)
    p.add_argument("--question", help="Poll question")
    p.add_argument("--options", help="Poll options: A,B,C")
    args = p.parse_args()

    if not args.token:
        print("[!] Set TG_BOT_TOKEN or use --token"); sys.exit(1)

    msg = args.message
    if args.message_file and os.path.exists(args.message_file):
        with open(args.message_file) as f:
            msg = f.read().strip()

    if args.action == "me":
        get_me_bot(args.token)
    elif args.action == "send":
        if not args.chat or not msg:
            print("[-] --chat and --message required"); sys.exit(1)
        r = send_message(args.chat, msg, token=args.token)
        print(f"[{'OK' if r.get('ok') else 'FAIL'}] Sent to {args.chat}")
    elif args.action == "broadcast":
        chat_ids = []
        if args.chats:
            with open(args.chats) as f:
                chat_ids = [l.strip() for l in f if l.strip()]
        elif args.chat:
            chat_ids = [args.chat]
        broadcast(chat_ids, msg or "Test broadcast", args.delay, args.photo_url, args.token)
    elif args.action == "schedule":
        if not args.chat or not msg:
            print("[-] --chat and --message required"); sys.exit(1)
        schedule_post(args.chat, msg, int(args.delay), args.photo_url, args.token)
    elif args.action == "stats":
        if not args.chat: print("[-] --chat required"); sys.exit(1)
        get_chat_stats(args.chat, args.token)
    elif args.action == "poll":
        if not args.chat or not args.question or not args.options:
            print("[-] --chat, --question, --options required"); sys.exit(1)
        opts = [o.strip() for o in args.options.split(",")]
        r = send_poll(args.chat, args.question, opts, token=args.token)
        print(f"[{'OK' if r.get('ok') else 'FAIL'}] Poll sent")
    elif args.action == "pin":
        if not args.chat or not args.message_id:
            print("[-] --chat and --message-id required"); sys.exit(1)
        pin_message(args.chat, args.message_id, token=args.token)
    elif args.action == "forward":
        if not args.from_chat or not args.chat:
            print("[-] --from-chat and --chat required"); sys.exit(1)
        ids = list(range(1, args.count + 1))  # Simplified: forward recent IDs
        forward_messages(args.from_chat, args.chat, ids, args.token)


if __name__ == "__main__":
    main()
