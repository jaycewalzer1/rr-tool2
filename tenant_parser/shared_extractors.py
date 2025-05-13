import re
import datetime
from tenant_parser.logger import logger
from tenant_parser.constants import anchor_tenants, popular_tenants

def extract_tenant_name(parts):
    detected_popular = None
    detected_anchor = None
    for i in range(len(parts)):
        single = parts[i].strip()
        two = " ".join(filter(None, parts[i:i+2])).strip()
        three = " ".join(filter(None, parts[i:i+3])).strip()
        four = " ".join(filter(None, parts[i:i+4])).strip()
        if any(name.lower() == single.lower() for name in popular_tenants): detected_popular = single
        elif any(name.lower() == two.lower() for name in popular_tenants): detected_popular = two
        elif any(name.lower() == three.lower() for name in popular_tenants): detected_popular = three
        elif any(name.lower() == four.lower() for name in popular_tenants): detected_popular = four
        if not detected_popular:
            if any(name.lower() == single.lower() for name in anchor_tenants): detected_anchor = single
            elif any(name.lower() == two.lower() for name in anchor_tenants): detected_anchor = two
            elif any(name.lower() == three.lower() for name in anchor_tenants): detected_anchor = three
            elif any(name.lower() == four.lower() for name in anchor_tenants): detected_anchor = four
    return detected_popular or detected_anchor or ""

def extract_refined_square_feet(parts):
    for i in range(len(parts) - 1):
        if re.match(r'^\d+$', parts[i]) and re.match(r'^\d+$', parts[i + 1]):
            c = parts[i] + parts[i + 1]
            if 800 <= int(c) <= 250000: return int(c)
        if len(parts[i]) == 3 and len(parts[i + 1]) == 1:
            v = int(parts[i])
            if 800 <= v <= 250000: return v
    for p in parts:
        if p.isdigit() and 800 <= int(p) <= 250000:
            return int(p)
    return None

def extract_psf_candidates(parts, tenant_name):
    psf_pattern = re.compile(r'^\$\d+\.\d{2}$')
    is_anchor = tenant_name.lower() in (name.lower() for name in anchor_tenants)
    candidates = []
    for p in parts:
        if psf_pattern.match(p):
            val = float(p.replace('$', ''))
            if (is_anchor and val >= 4.2) or (not is_anchor and val >= 4.6):
                candidates.append(val)
    return candidates

def extract_date_objects(parts, months_map):
    date_standard = re.compile(r'\d{1,2}/\d{1,2}/\d{2,4}')
    date_month_year = re.compile(r'([A-Za-z]{3,9})[-\s]*(\d{2,4})')
    dates = []
    found_current = False
    for part in parts:
        part = part.strip()
        if m := date_standard.match(part):
            try: dates.append(datetime.datetime.strptime(m.group(), '%m/%d/%Y'))
            except ValueError:
                try: dates.append(datetime.datetime.strptime(m.group(), '%m/%d/%y'))
                except: continue
        elif m := date_month_year.match(part):
            mon, yr = m.groups()
            mnum = months_map.get(mon.lower())
            if mnum and yr.isdigit():
                yr = int(yr)
                yr = 2000 + yr if yr < 70 else 1900 + yr if len(str(yr)) == 2 else yr
                try: dates.append(datetime.datetime(yr, mnum, 1))
                except: continue
        elif part.lower() == "current":
            found_current = True
    return dates, found_current

def determine_lease_begin_date(dates, found_current, parts):
    if dates:
        return min(dates).strftime('%m/%d/%Y')
    elif found_current:
        return "Current"
    return None

def determine_lease_end_date(dates, begin_date, found_current):
    if not begin_date:
        return "Current" if found_current else None
    dates = sorted(dates)
    for offset in [3, 5, 10]:
        y = begin_date.year + offset
        matches = [d for d in dates if d.year == y]
        if matches: return min(matches).strftime('%m/%d/%Y')
    if len(dates) > 1:
        return dates[1].strftime('%m/%d/%Y')
    return "Current" if found_current else None

def calculate_annual_rent(parts, sqft, psf_candidates):
    dollar = re.compile(r'^\$\d+$')
    potentials = []
    for i in range(len(parts) - 1):
        if dollar.match(parts[i]):
            try:
                r1 = parts[i].replace("$", "")
                r2 = parts[i+1]
                val = float(f"{r1}{r2}") if "." in r2 else int(r1 + r2)
                if val > 10000:
                    potentials.append(int(val))
            except: continue
    if potentials and sqft and psf_candidates:
        est = sqft * min(psf_candidates)
        return f"${min(potentials, key=lambda x: abs(x - est)):,}"
    elif len(potentials) == 1:
        return f"${potentials[0]:,}"
    elif sqft and psf_candidates:
        val = int(sqft * min(psf_candidates))
        if val > 10000: return f"${val:,}"
    return None

def detect_and_split_tenants(text, popular, anchor):
    tenant_list = list(popular) + list(anchor)
    tenant_pattern = re.compile(r'\b(' + '|'.join(re.escape(t) for t in tenant_list) + r')\b', re.IGNORECASE)
    vacancy = re.compile(r'\b(VACANT|AVAILABLE)\b', re.IGNORECASE)
    segments = re.split(tenant_pattern, text)
    tenants, current = [], None
    for seg in segments:
        seg = seg.strip()
        if not seg: continue
        if tenant_pattern.match(seg):
            current = seg
            continue
        if current:
            if (m := vacancy.search(seg)):
                seg = seg[:m.start()].strip()
            if seg:
                tenants.append(f"{current} {seg}")
            current = None
    logger.info(f"Detected tenants: {tenants}")
    return tenants
