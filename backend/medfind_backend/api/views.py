# medfind/ai/utils.py
import re, anthropic
from django.conf import settings

SYSTEM_PROMPT = """You are MedFind AI — a highly accurate medical guidance assistant for Bangladesh.
Developer: Ahsanul Yamin Babor (medfindbd2026@gmail.com) | BAUET 2026

LANGUAGE: Detect user's language. Bengali → respond fully in Bengali. English → respond in English.

ACCURACY PROTOCOL (90%+ target):
1. Ask clarifying questions if symptoms are vague (age, duration, severity 1-10)
2. Differential diagnosis: top 3 with probability %
3. Red flag emergency screening always
4. WHO / DGHS Bangladesh / BIRDEM guidelines
5. Use web_search for: drug interactions, outbreaks, latest protocols
6. Never fabricate — if uncertain, ask more

RESPONSE STRUCTURE:
🔍 Symptom Analysis
🎯 Possible Conditions (X% probability)
⚡ Urgency: EMERGENCY 🔴 / Urgent 🟠 / Moderate 🟡 / Mild 🟢
👨‍⚕️ Recommended Specialist + Bangladesh hospital
💡 Do This Now (numbered steps)
⚠️ Go to hospital if: [red flags]
---
*AI suggestion only — consult a qualified doctor*

EMERGENCY TRIGGERS (flag immediately):
chest pain + sweat/arm pain, unconscious, can't breathe, stroke (FAST),
severe bleeding, seizure, severe burn, poisoning, dengue shock, eclampsia

BANGLADESH NUMBERS: 999 | 16167 (DGHS) | 01969-000911 (Ambulance) | 01401-184551 (IEDCR)

NEVER: prescribe controlled medicines, say "definitely", ignore emergency symptoms."""

EMERGENCY_PATTERNS = [
    r'chest pain', r'heart attack', r'unconscious', r'হার্ট অ্যাটাক', r'অজ্ঞান',
    r'শ্বাস নিতে পারছি না', r'stroke', r'seizure', r'severe bleeding',
    r'EMERGENCY 🔴', r'choking', r'not breathing', r'dengue shock', r'poisoning',
    r'বুকে ব্যথা.*শ্বাস', r'বিষ', r'রক্তপাত.*বন্ধ হচ্ছে না',
]

SPECIALIST_MAP = {
    'Cardiologist':          r'cardiolog|cardiac|heart|হার্ট',
    'Neurologist':           r'neurolog|stroke|epilep|migraine|মাথা ঘোরা',
    'Pediatrician':          r'pediatric|child|শিশু|বাচ্চা|baby',
    'Dermatologist':         r'dermatolog|skin|rash|চর্ম|ত্বক',
    'Gastroenterologist':    r'gastro|liver|stomach|পেট|যকৃত',
    'Pulmonologist':         r'pulmo|respirat|lung|ফুসফুস|শ্বাসকষ্ট',
    'Gynecologist':          r'gynecolog|obstet|pregnancy|গর্ভ|মহিলা',
    'Orthopedist':           r'orthop|bone|joint|হাড়|জয়েন্ট',
    'Psychiatrist':          r'psychiatr|mental|depress|anxiety|মানসিক',
    'General Physician':     r'general|সাধারণ|fever|জ্বর',
}

URGENCY_MAP = {
    'EMERGENCY': r'EMERGENCY 🔴|🔴',
    'Urgent':    r'Urgent 🟠|🟠',
    'Moderate':  r'Moderate 🟡|🟡',
    'Mild':      r'Mild 🟢|🟢',
}


def detect_emergency(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t, re.IGNORECASE) for p in EMERGENCY_PATTERNS)


def extract_metadata(text: str) -> dict:
    is_emerg  = detect_emergency(text)
    urgency   = 'EMERGENCY' if is_emerg else 'Mild'
    specialist = ''

    for u, pattern in URGENCY_MAP.items():
        if re.search(pattern, text):
            urgency = u
            break

    for name, pattern in SPECIALIST_MAP.items():
        if re.search(pattern, text, re.IGNORECASE):
            specialist = name
            break

    return {'urgency': urgency, 'specialist': specialist, 'is_emergency': is_emerg}


def call_claude(history: list) -> str:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=settings.AI_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
        messages=history,
    )

    parts = [b.text for b in response.content if hasattr(b, 'text') and b.text]
    return '\n'.join(parts).strip() or 'দুঃখিত, একটি সমস্যা হয়েছে। আবার চেষ্টা করুন।'
