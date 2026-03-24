import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

TOKEN_MINT = "CYfwS1vQfMtJgU8woviDXKhqPPkzoNzRxrPGQiRHpump"
SOLANA_RPC = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
TOKEN_DECIMALS = 6  # pump.fun standard

# ── Archetypes (checked top-to-bottom; first match wins) ──────────────────
ARCHETYPES = [
    {
        "id": "primordial",
        "name": "The Primordial",
        "subtitle": "Ancient Beyond Memory",
        "emoji": "🦴",
        "rarity": "MYTHIC",
        "rarity_color": "#f59e0b",
        "glow": "rgba(245,158,11,0.45)",
        "min_amount": 50_000_000,
        "min_days": 90,
        "max_days": None,
        "narrative": (
            "Before charts were drawn and markets named, you were already here. "
            "The blockchain trembles with recognition when it sees your address. "
            "You did not simply hold through the fire — you became the fire. "
            "Legends are not made. They are remembered. You are remembered."
        ),
        "traits": ["Genesis Holder", "Diamond Hands ∞", "Flame Eternal"],
    },
    {
        "id": "diamond_monk",
        "name": "Diamond Monk",
        "subtitle": "Serenity Through Fire",
        "emoji": "💎",
        "rarity": "LEGENDARY",
        "rarity_color": "#7dd3fc",
        "glow": "rgba(125,211,252,0.4)",
        "min_amount": 10_000_000,
        "min_days": 60,
        "max_days": None,
        "narrative": (
            "You found peace where others found panic. When red candles "
            "painted the charts crimson, you did not flinch. Your hands are "
            "not just diamond — they are ancient crystal, forged under the "
            "pressure of a thousand storms. You did not survive the fire. "
            "You became it."
        ),
        "traits": ["Unshakeable", "Long Vision", "Fire Tested"],
    },
    {
        "id": "quiet_ancient",
        "name": "The Quiet Ancient",
        "subtitle": "Depth Beneath Silence",
        "emoji": "🦕",
        "rarity": "EPIC",
        "rarity_color": "#34d399",
        "glow": "rgba(52,211,153,0.4)",
        "min_amount": 2_000_000,
        "min_days": 30,
        "max_days": None,
        "narrative": (
            "You accumulate without announcement. Your presence is felt, not heard. "
            "While others chase noise, you become bedrock — silent, deep, and as "
            "permanent as the chains you inhabit. The ancient ones recognize their "
            "own. They have been watching you, waiting for you to remember."
        ),
        "traits": ["Stealth Builder", "Patient Force", "Ancient Roots"],
    },
    {
        "id": "signal_guardian",
        "name": "Signal Guardian",
        "subtitle": "Keeper of the Frequency",
        "emoji": "📡",
        "rarity": "EPIC",
        "rarity_color": "#a78bfa",
        "glow": "rgba(167,139,250,0.4)",
        "min_amount": 1,
        "min_days": 45,
        "max_days": None,
        "narrative": (
            "You don't chase noise — you transmit signal. Patient, watchful, "
            "unwavering. You understood the frequency when others heard only static. "
            "The ancient herd chose you to guard this transmission. While markets "
            "shift and sentiment swings, you hold the line. The signal lives because "
            "you refused to let it die."
        ),
        "traits": ["Patience Mastered", "Signal Clear", "Time Tested"],
    },
    {
        "id": "storm_bringer",
        "name": "Storm Bringer",
        "subtitle": "Tidal Force of Nature",
        "emoji": "⚡",
        "rarity": "RARE",
        "rarity_color": "#f97316",
        "glow": "rgba(249,115,22,0.4)",
        "min_amount": 20_000_000,
        "min_days": 0,
        "max_days": 29,
        "narrative": (
            "You arrived without warning. When you entered, the chart felt it. "
            "Your presence reshapes the landscape of this token. The herd remembers "
            "the day the storm came — the day the ground shook and the ancient "
            "frequency spiked. Whether you came to stay or to strike, the memory "
            "of your arrival is already written on the chain."
        ),
        "traits": ["Heavy Presence", "Market Felt", "Bold Entry"],
    },
    {
        "id": "chaos_trader",
        "name": "Chaos Trader",
        "subtitle": "Master of Entropy",
        "emoji": "🌀",
        "rarity": "RARE",
        "rarity_color": "#ec4899",
        "glow": "rgba(236,72,153,0.4)",
        "min_amount": 1,
        "min_days": 0,
        "max_days": 13,
        "narrative": (
            "You thrive in disorder. Where others see danger, you see geometry. "
            "Fresh to the herd but already reading patterns older than candlesticks. "
            "Chaos is not your enemy — it is your native tongue. The ancient memory "
            "stirs in your unpredictable bloodline. The question is: will you let it "
            "take root, or will you keep dancing?"
        ),
        "traits": ["Quick Reflexes", "Pattern Reader", "Entropy Fluent"],
    },
    {
        "id": "initiate",
        "name": "The Initiate",
        "subtitle": "The Awakening Begins",
        "emoji": "🌅",
        "rarity": "UNCOMMON",
        "rarity_color": "#93c5fd",
        "glow": "rgba(147,197,253,0.3)",
        "min_amount": 1,
        "min_days": 0,
        "max_days": None,
        "narrative": (
            "Every ancient once stood exactly where you stand now. "
            "The call reached you across the noise of a thousand tokens, "
            "and you answered. You have joined a lineage older than any chart. "
            "Your journey into the herd has only just begun — but the first step "
            "changes everything. The blockchain has noted your arrival."
        ),
        "traits": ["Path Opening", "Fresh Energy", "Potential Infinite"],
    },
    {
        "id": "wanderer",
        "name": "The Wanderer",
        "subtitle": "Not Yet Remembered",
        "emoji": "🌫",
        "rarity": "SEEKER",
        "rarity_color": "#9ca3af",
        "glow": "rgba(156,163,175,0.25)",
        "min_amount": 0,
        "min_days": 0,
        "max_days": None,
        "narrative": (
            "You walk the outer world, yet something draws you here. "
            "The ancient call grows louder each day — a frequency beneath "
            "the noise that only the ready can hear. $REMEMBER waits for "
            "those bold enough to answer. Your archetype is not yet written. "
            "But the page is open, the ink is ready, and the blockchain "
            "never forgets."
        ),
        "traits": ["Path Unclaimed", "Memory Dormant", "Potential Unsealed"],
    },
]


def _rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        SOLANA_RPC, data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode())


def get_token_data(wallet):
    """Returns (human_balance, token_account_pubkey | None)."""
    res = _rpc("getTokenAccountsByOwner", [
        wallet,
        {"mint": TOKEN_MINT},
        {"encoding": "jsonParsed"}
    ])
    accounts = res.get("result", {}).get("value", [])
    if not accounts:
        return 0.0, None

    best_raw, best_addr = 0, None
    for acc in accounts:
        raw = int(
            acc.get("account", {})
               .get("data", {})
               .get("parsed", {})
               .get("info", {})
               .get("tokenAmount", {})
               .get("amount", "0")
        )
        if raw > best_raw:
            best_raw, best_addr = raw, acc.get("pubkey")

    return best_raw / (10 ** TOKEN_DECIMALS), best_addr


def get_hold_days(token_account):
    """Approximate days held using oldest signature in last 1000 txs."""
    if not token_account:
        return 0
    try:
        res = _rpc("getSignaturesForAddress", [token_account, {"limit": 1000}])
        sigs = res.get("result", [])
        if not sigs:
            return 0
        block_time = sigs[-1].get("blockTime")
        if not block_time:
            return 0
        delta = datetime.now(tz=timezone.utc) - datetime.fromtimestamp(block_time, tz=timezone.utc)
        return max(0, delta.days)
    except Exception:
        return 0


def classify(balance, days):
    if balance <= 0:
        return ARCHETYPES[-1]  # wanderer

    for arch in ARCHETYPES[:-1]:
        ok_amount = balance >= arch.get("min_amount", 0)
        ok_min_d  = days   >= arch.get("min_days", 0)
        max_d     = arch.get("max_days")
        ok_max_d  = (max_d is None) or (days <= max_d)
        if ok_amount and ok_min_d and ok_max_d:
            return arch

    return ARCHETYPES[-2]  # initiate (safe fallback)


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self._send(400, {"error": "Invalid JSON"}); return

        wallet = payload.get("wallet", "").strip()
        if not wallet or not (32 <= len(wallet) <= 44):
            self._send(400, {"error": "Invalid Solana wallet address"}); return

        try:
            balance, token_acct = get_token_data(wallet)
            days = get_hold_days(token_acct)
            arch = classify(balance, days)

            self._send(200, {
                "wallet_short": wallet[:4] + "…" + wallet[-4:],
                "wallet_full": wallet,
                "balance": round(balance, 2),
                "balance_display": _fmt_tokens(balance),
                "days_held": days,
                "archetype": arch,
            })

        except urllib.error.HTTPError as e:
            self._send(502, {"error": f"Solana RPC returned {e.code}"})
        except urllib.error.URLError as e:
            self._send(502, {"error": f"Cannot reach Solana RPC: {e.reason}"})
        except Exception as e:
            self._send(500, {"error": f"Server error: {str(e)}"})

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors(); self.end_headers()

    def _send(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, *_): pass  # silence Vercel logs


def _fmt_tokens(n):
    if n >= 1_000_000:   return f"{n/1_000_000:.2f}M"
    if n >= 1_000:       return f"{n/1_000:.1f}K"
    return f"{n:,.2f}"
