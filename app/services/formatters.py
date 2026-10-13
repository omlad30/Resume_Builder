import re

def clean_bullets(text):
    """Normalizes bullet characters to clean lines without messy artifacts."""
    if not text:
        return []
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading bullet glyphs
        clean = re.sub(r'^[\s\x95\u2022\*\-\·\–]+\s*', '', line).strip()
        if clean:
            cleaned_lines.append(clean)
    return cleaned_lines

def parse_skills(text):
    """
    Parses skills text.
    If categorized (e.g. 'Languages: Python, Java'), returns list of (category, items_str).
    Otherwise returns [('', text)].
    """
    if not text:
        return []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    categorized = []
    has_categories = any(':' in l for l in lines)
    if has_categories:
        for line in lines:
            if ':' in line:
                cat, val = line.split(':', 1)
                categorized.append((cat.strip(), val.strip()))
            else:
                categorized.append(('', line.strip()))
        return categorized
    else:
        # Check if single line comma separated
        return [('', text.strip())]

def parse_education(text):
    """
    Parses education entries into:
    [{'degree': '...', 'date': '...', 'subtitle': '...', 'bullets': [...]}]
    """
    if not text:
        return []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    entries = []
    i = 0
    date_regex = re.compile(
        r'(\b(?:19|20)\d{2}\s*[-–—]\s*(?:(?:19|20)\d{2}|Present|Expected|\b\d{4}\b(?:\s*\(Expected\))?|\w+).*)$|'
        r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b.*)$',
        re.I
    )

    while i < len(lines):
        line = lines[i]
        # Skip if starting with bullet (sub-item)
        if re.match(r'^[\s\x95\u2022\*\-\·]', line) and entries:
            clean = re.sub(r'^[\s\x95\u2022\*\-\·]+\s*', '', line).strip()
            entries[-1]['bullets'].append(clean)
            i += 1
            continue

        # Look for date in line
        date = ""
        degree = line
        m = date_regex.search(line)
        if m:
            date = m.group(0).strip()
            degree = line[:m.start()].strip()
            # Clean trailing pipes or hyphens
            degree = re.sub(r'[\s|–—\-]+$', '', degree).strip()

        # Next line might be university / institution & CGPA
        subtitle = ""
        bullets = []
        if i + 1 < len(lines) and not date_regex.search(lines[i + 1]) and not re.match(r'^[\s\x95\u2022\*\-\·]', lines[i + 1]):
            # If line has date or looks like sub-info
            subtitle = lines[i + 1]
            i += 2
        else:
            i += 1

        entries.append({
            'degree': degree or line,
            'date': date,
            'subtitle': subtitle,
            'bullets': bullets
        })

    return entries

def parse_projects(text):
    """
    Parses project entries:
    [{'title': '...', 'links': '...', 'tech_stack': '...', 'bullets': [...]}]
    """
    if not text:
        return []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    projects = []
    current_proj = None

    for line in lines:
        is_bullet = bool(re.match(r'^[\s\x95\u2022\*\-\·]', line))
        is_tech = bool(re.match(r'^(?:tech(?:\s*stack)?|technologies|built with):\s*', line, re.I))

        if is_tech and current_proj:
            tech_val = re.sub(r'^(?:tech(?:\s*stack)?|technologies|built with):\s*', '', line, flags=re.I).strip()
            current_proj['tech_stack'] = tech_val
        elif is_bullet and current_proj:
            bullet_clean = re.sub(r'^[\s\x95\u2022\*\-\·]+\s*', '', line).strip()
            current_proj['bullets'].append(bullet_clean)
        else:
            # New Project Title line
            parts = [p.strip() for p in line.split('|')]
            title = parts[0]
            links = " | ".join(parts[1:]) if len(parts) > 1 else ""

            current_proj = {
                'title': title,
                'links': links,
                'tech_stack': '',
                'bullets': []
            }
            projects.append(current_proj)

    return projects

def parse_experience(text):
    """
    Parses experience / internships:
    [{'role_company': '...', 'date': '...', 'bullets': [...]}]
    """
    if not text:
        return []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    entries = []
    current_entry = None
    date_regex = re.compile(
        r'(\b(?:19|20)\d{2}\s*[-–—]\s*(?:(?:19|20)\d{2}|Present|Expected|\b\d{4}\b|\w+).*)$|'
        r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(?:\d{4})?(?:\s*[-–—]\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*)?\d{4}|Present)?.*)$',
        re.I
    )

    for line in lines:
        is_bullet = bool(re.match(r'^[\s\x95\u2022\*\-\·]', line))
        is_tech = bool(re.match(r'^(?:tech(?:\s*stack)?|technologies|built with):\s*', line, re.I))

        if is_tech and current_entry:
            tech_val = re.sub(r'^(?:tech(?:\s*stack)?|technologies|built with):\s*', '', line, flags=re.I).strip()
            current_entry['tech_stack'] = tech_val
        elif is_bullet and current_entry:
            clean = re.sub(r'^[\s\x95\u2022\*\-\·]+\s*', '', line).strip()
            current_entry['bullets'].append(clean)
        else:
            # Check for date in header
            m = date_regex.search(line)
            date = ""
            header = line
            if m:
                date = m.group(0).strip()
                header = line[:m.start()].strip()
                header = re.sub(r'[\s|–—\-]+$', '', header).strip()

            current_entry = {
                'role_company': header or line,
                'date': date,
                'tech_stack': '',
                'bullets': []
            }
            entries.append(current_entry)

    return entries
