SECTION_RANGES = [
    ('PURE AI',   1,  25),
    ('AI+DEV',   26,  30),
    ('AI+CYBER', 31,  35),
    ('PURE WEB', 36,  60),
    ('WEB+CYBER', 61, 65),
    ('WEB+DEV',  66,  70),
    ('DBMS',     71,  75),
]

SECTION_TOTALS = {
    'PURE AI': 25, 'AI+DEV': 5, 'AI+CYBER': 5,
    'PURE WEB': 25, 'WEB+CYBER': 5, 'WEB+DEV': 5, 'DBMS': 5,
}

# Max possible scores per section per domain (cross-domain = 2x, DBMS is neutral 1x for both)
SECTION_TOTALS_BY_DOMAIN = {
    'AIML': {
        'PURE AI': 25, 'AI+DEV': 5,  'AI+CYBER': 5,
        'PURE WEB': 50, 'WEB+CYBER': 10, 'WEB+DEV': 10, 'DBMS': 5,
    },
    'Web & App Dev': {
        'PURE AI': 50, 'AI+DEV': 10, 'AI+CYBER': 10,
        'PURE WEB': 25, 'WEB+CYBER': 5,  'WEB+DEV': 5,  'DBMS': 5,
    },
}

AI_SECTIONS  = {'PURE AI', 'AI+DEV', 'AI+CYBER'}
WEB_SECTIONS = {'PURE WEB', 'WEB+CYBER', 'WEB+DEV'}


def get_question_section(question_no):
    for name, start, end in SECTION_RANGES:
        if start is not None and start <= question_no <= end:
            return name
    return None


def get_multiplier(domain, section):
    """Return 2 if the question is cross-domain for this participant, else 1."""
    if section is None:
        return 1
    if domain == 'AIML' and section in WEB_SECTIONS:
        return 2
    if domain == 'Web & App Dev' and section in AI_SECTIONS:
        return 2
    return 1
