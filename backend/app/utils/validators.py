import re


PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)


def normalize_optional_text(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def normalize_email(value):
    value = normalize_optional_text(value)
    return value.lower() if value else None


def is_valid_phone(value):
    return bool(value and PHONE_PATTERN.fullmatch(value))


def is_valid_email(value):
    if not value or len(value) > 254:
        return False
    if not EMAIL_PATTERN.fullmatch(value):
        return False

    local_part, domain = value.rsplit('@', 1)
    if '..' in local_part:
        return False

    for label in domain.split('.'):
        if not label or label.startswith('-') or label.endswith('-'):
            return False

    return True
