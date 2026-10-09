import random
import re
from dataclasses import dataclass

from .sources.base import Candidate

# model keyword -> (brand, display model)
MODELS = {
    "mustang": ("Ford", "Mustang"),
    "thunderbird": ("Ford", "Thunderbird"),
    "model t": ("Ford", "Model T"),
    "model a": ("Ford", "Model A"),
    "corvette": ("Chevrolet", "Corvette"),
    "camaro": ("Chevrolet", "Camaro"),
    "impala": ("Chevrolet", "Impala"),
    "bel air": ("Chevrolet", "Bel Air"),
    "chevelle": ("Chevrolet", "Chevelle"),
    "nova": ("Chevrolet", "Nova"),
    "gto": ("Pontiac", "GTO"),
    "firebird": ("Pontiac", "Firebird"),
    "trans am": ("Pontiac", "Trans Am"),
    "charger": ("Dodge", "Charger"),
    "challenger": ("Dodge", "Challenger"),
    "road runner": ("Plymouth", "Road Runner"),
    "superbird": ("Plymouth", "Superbird"),
    "cuda": ("Plymouth", "Barracuda"),
    "barracuda": ("Plymouth", "Barracuda"),
    "eldorado": ("Cadillac", "Eldorado"),
    "deville": ("Cadillac", "DeVille"),
    "continental": ("Lincoln", "Continental"),
    "beetle": ("Volkswagen", "Beetle"),
    "kafer": ("Volkswagen", "Beetle"),
    "käfer": ("Volkswagen", "Beetle"),
    "bulli": ("Volkswagen", "T1 Bus"),
    "karmann": ("Volkswagen", "Karmann Ghia"),
    "911": ("Porsche", "911"),
    "356": ("Porsche", "356"),
    "914": ("Porsche", "914"),
    "e-type": ("Jaguar", "E-Type"),
    "e type": ("Jaguar", "E-Type"),
    "300sl": ("Mercedes-Benz", "300 SL"),
    "gullwing": ("Mercedes-Benz", "300 SL Gullwing"),
    "pagoda": ("Mercedes-Benz", "SL Pagoda"),
    "2cv": ("Citroen", "2CV"),
    "ds": ("Citroen", "DS"),
    "mini cooper": ("Mini", "Cooper"),
    "500": ("Fiat", "500"),
    "db5": ("Aston Martin", "DB5"),
    "silver cloud": ("Rolls-Royce", "Silver Cloud"),
}

BRANDS = {
    "chevrolet": "Chevrolet", "chevy": "Chevrolet", "ford": "Ford", "cadillac": "Cadillac",
    "pontiac": "Pontiac", "dodge": "Dodge", "plymouth": "Plymouth", "buick": "Buick",
    "oldsmobile": "Oldsmobile", "lincoln": "Lincoln", "chrysler": "Chrysler", "packard": "Packard",
    "studebaker": "Studebaker", "mercedes": "Mercedes-Benz", "porsche": "Porsche",
    "volkswagen": "Volkswagen", "vw": "Volkswagen", "jaguar": "Jaguar", "ferrari": "Ferrari",
    "bmw": "BMW", "alfa": "Alfa Romeo", "rolls": "Rolls-Royce", "bentley": "Bentley",
    "citroen": "Citroen", "citroën": "Citroen", "fiat": "Fiat", "aston": "Aston Martin",
    "lancia": "Lancia", "triumph": "Triumph", "mg": "MG", "austin": "Austin", "opel": "Opel",
    "volvo": "Volvo", "shelby": "Shelby", "lamborghini": "Lamborghini", "bugatti": "Bugatti",
}

SOUND_HOOKS = ["Pure Engine Sound", "Sound On", "Listen to That Engine", "Classic Sound, No Talking"]
VISUAL_HOOKS = ["Timeless Design", "Golden Era Beauty", "Chrome and Curves", "Old School Cool", "Pure Classic Style"]

SOUND_LINES = [
    "Turn the sound up and enjoy the real engine sound of this classic.",
    "No talking, just the sound of a real classic car.",
]
VISUAL_LINES = [
    "A few seconds of pure classic car design, from the bodylines to the chrome details.",
    "Timeless lines and real vintage character in one short clip.",
    "The golden era of motoring, one classic at a time.",
]

GENERIC_NAMES = ["Vintage Classic Car", "Classic Car", "Old School Classic", "Vintage Oldtimer"]
MUSCLE_NAMES = ["Classic American Muscle Car", "Vintage Muscle Car"]


@dataclass
class Metadata:
    title: str
    description: str
    tags: list[str]
    language: str = "en"


def _has(text: str, key: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])", text) is not None


def identify(text: str) -> tuple[str | None, str | None, str | None]:
    text = text.lower()
    year = None
    m = re.search(r"\b(19[2-8]\d)\b", text)
    if m:
        year = m.group(1)
    else:
        m = re.search(r"\b(?:19)?([2-8]0)'?s\b", text)
        if m:
            year = f"19{m.group(1)}s"

    brand = model = None
    for key in sorted(MODELS, key=len, reverse=True):
        if _has(text, key) and (len(key) > 3 or any(_has(text, b) for b, v in BRANDS.items() if v == MODELS[key][0])):
            brand, model = MODELS[key]
            break
    if brand is None:
        for key, name in BRANDS.items():
            if _has(text, key):
                brand = name
                break
    return year, brand, model


def _hashtag(value: str) -> str:
    return "#" + re.sub(r"[^A-Za-z0-9]", "", value).lower()


def build(cand: Candidate, music_added: bool, music_credit: str) -> Metadata:
    text = cand.text()
    year, brand, model = identify(text)

    if brand and model:
        name = " ".join(p for p in (year, brand, model) if p)
    elif brand:
        name = " ".join(p for p in (year, "Classic", brand) if p)
    else:
        pool = MUSCLE_NAMES if "muscle" in text else GENERIC_NAMES
        name = " ".join(p for p in (year, random.choice(pool)) if p)

    hook = random.choice(VISUAL_HOOKS if music_added else SOUND_HOOKS)
    title = f"{name} | {hook}"[:100]

    lines = [random.choice(VISUAL_LINES if music_added else SOUND_LINES), ""]
    lines.append("Subscribe to Retro Garage for daily classic car Shorts.")
    lines.append("")

    credit = f"Footage: {cand.page_url}"
    if cand.author:
        credit += f" by {cand.author}"
    credit += f" ({cand.license.name}"
    if cand.license.url:
        credit += f", {cand.license.url}"
    credit += ")"
    lines.append(credit)
    if music_added and music_credit:
        lines.append(music_credit)
    lines.append("")

    hashtags = ["#shorts", "#classiccars", "#vintagecars"]
    if model:
        hashtags.append(_hashtag(model))
    elif brand:
        hashtags.append(_hashtag(brand))
    else:
        hashtags.append("#oldtimer")
    lines.append(" ".join(hashtags))

    tags = ["classic cars", "vintage cars", "oldtimer", "retro garage", "classic car shorts", "car shorts"]
    if "muscle" in text:
        tags.append("muscle car")
    for value in (brand, model, f"{brand} {model}" if brand and model else None, year):
        if value and value.lower() not in tags:
            tags.append(value.lower())
    if not music_added:
        tags += ["engine sound", "car sound"]
    trimmed, total = [], 0
    for tag in tags:
        if total + len(tag) + 1 > 480:
            break
        trimmed.append(tag)
        total += len(tag) + 1

    return Metadata(title=title, description="\n".join(lines), tags=trimmed)
