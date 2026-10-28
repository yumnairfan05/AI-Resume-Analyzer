"""Combine skills, semantic match and CV quality checks into one report."""
import re

from .matcher import semantic_match
from .skills import extract_skills

SECTION_PATTERNS = {
    "Summary": r"\b(summary|profile|objective|about me)\b",
    "Experience": r"\b(experience|employment|work history|internship)\b",
    "Education": r"\b(education|academic|university|degree)\b",
    "Skills": r"\b(skills|technologies|tech stack|tools)\b",
    "Projects": r"\b(projects?|portfolio)\b",
}


def _quality_checks(cv_text: str):
    lowered = cv_text.lower()
    words = len(cv_text.split())
    checks = []

    def add(label, ok, tip):
        checks.append({"label": label, "ok": ok, "tip": tip})

    for name, pattern in SECTION_PATTERNS.items():
        add(f"{name} section", bool(re.search(pattern, lowered)),
            f"Add a clear '{name}' heading so recruiters and ATS parsers can find it.")

    add("Email address", bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", cv_text)),
        "Add a professional email address at the top.")
    add("GitHub or LinkedIn link", ("github.com" in lowered) or ("linkedin.com" in lowered),
        "Link your GitHub and/or LinkedIn profile.")

    numbers = len(re.findall(r"\d+\s?%|\$\s?\d+|\b\d{2,}\b", cv_text))
    add("Measurable results", numbers >= 4,
        "Add numbers to your bullets (e.g. 'cut load time by 35%', 'served 2,000 users').")
    add("Reasonable length", 250 <= words <= 1000,
        "Aim for roughly 300-800 words, ideally one to two pages.")

    return checks, words


def analyze(cv_text: str, jd_text: str) -> dict:
    cv_skills = extract_skills(cv_text)
    jd_skills = extract_skills(jd_text)
    matched = sorted(cv_skills & jd_skills)
    missing = sorted(jd_skills - cv_skills)
    extra = sorted(cv_skills - jd_skills)

    skill_cov = len(matched) / len(jd_skills) if jd_skills else None
    sem = semantic_match(cv_text, jd_text)
    checks, words = _quality_checks(cv_text)
    quality = sum(c["ok"] for c in checks) / len(checks)

    if skill_cov is None:
        overall = 0.75 * sem["score"] + 0.25 * quality
    else:
        overall = 0.45 * skill_cov + 0.40 * sem["score"] + 0.15 * quality
    overall_pct = round(overall * 100)

    if overall_pct >= 75:
        verdict = "Strong match"
    elif overall_pct >= 55:
        verdict = "Good match, with gaps"
    elif overall_pct >= 35:
        verdict = "Partial match"
    else:
        verdict = "Weak match"

    suggestions = []
    for skill in missing[:6]:
        suggestions.append(
            f"The job asks for {skill}, but your CV doesn't mention it. If you have used it, "
            f"add it to your skills and show it in a project or job bullet. "
            f"If not, consider a small project that uses it."
        )
    for line, _ in sem["gaps"][:3]:
        short = line if len(line) <= 140 else line[:137] + "..."
        suggestions.append(
            f"Nothing in your CV closely answers this requirement: \"{short}\". "
            f"Add a bullet that shows relevant work."
        )
    for c in checks:
        if not c["ok"]:
            suggestions.append(c["tip"])
    if not suggestions:
        suggestions.append("Your CV lines up well with this job. Tailor the summary to its title and keywords.")

    return {
        "overall": overall_pct,
        "verdict": verdict,
        "skill_score": None if skill_cov is None else round(skill_cov * 100),
        "semantic_score": round(sem["score"] * 100),
        "quality_score": round(quality * 100),
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "gaps": sem["gaps"],
        "checks": checks,
        "suggestions": suggestions,
        "words": words,
    }


def build_report(result: dict) -> str:
    lines = [
        "AI RESUME ANALYSIS",
        "=" * 40,
        f"Overall match: {result['overall']}%  ({result['verdict']})",
        f"Skill coverage: {result['skill_score'] if result['skill_score'] is not None else 'n/a'}",
        f"Semantic fit: {result['semantic_score']}%",
        f"CV quality: {result['quality_score']}%",
        "",
        "Matched skills: " + (", ".join(result["matched"]) or "none"),
        "Missing skills: " + (", ".join(result["missing"]) or "none"),
        "",
        "Suggestions:",
    ]
    lines += [f"{i}. {s}" for i, s in enumerate(result["suggestions"], 1)]
    return "\n".join(lines)
