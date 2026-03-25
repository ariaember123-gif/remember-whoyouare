import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

REMEMBER_MINT = "CYfwS1vQfMtJgU8woviDXKhqPPkzoNzRxrPGQiRHpump"
RPC_URL = "https://api.mainnet-beta.solana.com"

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def get_token_data(wallet):
    # Get token accounts for wallet filtered by mint
    res = rpc("getTokenAccountsByOwner", [
        wallet,
        {"mint": REMEMBER_MINT},
        {"encoding": "jsonParsed"}
    ])
    accounts = res.get("result", {}).get("value", [])
    if not accounts:
        return 0, None

    total = 0
    oldest_ts = None
    pubkeys = []
    for acc in accounts:
        info = acc["account"]["data"]["parsed"]["info"]
        amt = int(info["tokenAmount"]["amount"])
        total += amt
        pubkeys.append(acc["pubkey"])

    total_ui = total / 1_000_000  # 6 decimals

    # Get oldest transaction for first account
    if pubkeys:
        sig_res = rpc("getSignaturesForAddress", [pubkeys[0], {"limit": 1000}])
        sigs = sig_res.get("result", [])
        if sigs:
            oldest_ts = sigs[-1].get("blockTime")

    return total_ui, oldest_ts


def classify(amount, days_held):
    # Archetypes ordered from rarest to most common
    archetypes = [
        {
            "name": "The Eternal Witness",
            "emoji": "🌌",
            "threshold_tokens": 50_000_000,
            "threshold_days": 90,
            "title": "Eternal Witness",
            "subtitle": "Bearer of Ancient Memory",
            "color": "#c084fc",
            "narrative": (
                "Since before the charts were drawn, you were here. "
                "You do not merely hold $REMEMBER — you ARE the memory. "
                "The blockchain whispers your name in every block, every burn, every transaction. "
                "Civilisations rise and fall, but your conviction does not waver. "
                "You are the eternal flame that cannot be extinguished."
            ),
            "power": "Temporal Mastery",
            "rarity": "Mythic · Top 0.1%",
        },
        {
            "name": "Diamond Monk",
            "emoji": "💎",
            "threshold_tokens": 10_000_000,
            "threshold_days": 60,
            "title": "Diamond Monk",
            "subtitle": "Seeker of Crystalline Truth",
            "color": "#7dd3fc",
            "narrative": (
                "Through corrections and chaos, you did not flinch. "
                "Your hands are not flesh — they are diamond, forged in the fire of a thousand red candles. "
                "The monks of old shaved their heads and turned from worldly noise. "
                "You turned from fear. You held. You remembered. "
                "Now the ancient power of $REMEMBER flows through you unimpeded."
            ),
            "power": "Unbreakable Conviction",
            "rarity": "Legendary · Top 1%",
        },
        {
            "name": "Signal Guardian",
            "emoji": "🔮",
            "threshold_tokens": 1_000_000,
            "threshold_days": 30,
            "title": "Signal Guardian",
            "subtitle": "Keeper of the Sacred Frequency",
            "color": "#a78bfa",
            "narrative": (
                "In a world drowning in noise, you hear the signal. "
                "You are the lighthouse on the dark blockchain shore — steady, unwavering, luminous. "
                "Others panic at shadows; you read the stars. "
                "$REMEMBER chose you as its guardian, and the community feels safer knowing you walk among them. "
                "Your presence alone raises the frequency of the entire herd."
            ),
            "power": "Clarity & Foresight",
            "rarity": "Epic · Top 5%",
        },
        {
            "name": "The Ancient",
            "emoji": "🦖",
            "threshold_tokens": 500_000,
            "threshold_days": 14,
            "title": "The Ancient",
            "subtitle": "First Mover of the Primordial Age",
            "color": "#4ade80",
            "narrative": (
                "You arrived when the land was still being shaped. "
                "The fossils tell your story — an early adopter who saw the dinosaur's power before the masses stampeded. "
                "Like the great beasts who walked before man, you claimed your territory with patience and primal instinct. "
                "The latecomers will one day speak of those like you in hushed, reverent tones."
            ),
            "power": "Primordial Instinct",
            "rarity": "Rare · Top 10%",
        },
        {
            "name": "Chaos Trader",
            "emoji": "⚡",
            "threshold_tokens": 100_000,
            "threshold_days": 0,
            "title": "Chaos Trader",
            "subtitle": "Rider of Volatile Winds",
            "color": "#f97316",
            "narrative": (
                "You do not walk the path — you ARE the storm. "
                "Where others see risk, you see opportunity dancing in the thunder. "
                "Your trades move fast, your spirit moves faster. "
                "The market bends to your chaos, and sometimes — just sometimes — the chaos bends back. "
                "Yet something made you hold $REMEMBER today, and that is no accident. "
                "The ancient call is working on you."
            ),
            "power": "Volatile Momentum",
            "rarity": "Uncommon · Top 20%",
        },
        {
            "name": "The Awakening",
            "emoji": "🌅",
            "threshold_tokens": 0,
            "threshold_days": 0,
            "title": "The Awakening",
            "subtitle": "One Who Has Just Begun to Remember",
            "color": "#38bdf8",
            "narrative": (
                "Every legend began with a single step. Every giant was once a sapling. "
                "You have heard the call of $REMEMBER and you answered — that alone sets you apart from the billions who sleep. "
                "Your archetype is not fixed. It is clay. "
                "Hold longer. Stack deeper. Let the memory crystallise within you. "
                "The dinosaur inside you is still stretching its wings. "
                "Soon, it will roar."
            ),
            "power": "Raw Potential",
            "rarity": "Common · The Beginning",
        },
    ]

    for arch in archetypes:
        if amount >= arch["threshold_tokens"] and days_held >= arch["threshold_days"]:
            return arch

    return archetypes[-1]


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        wallet = payload.get("wallet", "").strip()
        if not wallet or len(wallet) < 32:
            self._respond(400, {"error": "Invalid wallet address"})
            return

        try:
            amount, oldest_ts = get_token_data(wallet)
        except Exception as e:
            self._respond(502, {"error": f"RPC error: {str(e)}"})
            return

        now = datetime.now(timezone.utc).timestamp()
        if oldest_ts:
            days_held = int((now - oldest_ts) / 86400)
        else:
            days_held = 0

        archetype = classify(amount, days_held)

        self._respond(200, {
            "wallet": wallet[:6] + "…" + wallet[-4:],
            "amount": amount,
            "amount_display": f"{amount:,.0f}",
            "days_held": days_held,
            "has_tokens": amount > 0,
            "archetype": archetype,
        })

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def _respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
