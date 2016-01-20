
CRITICAL_SEV_CODE = 1
MAJOR_SEV_CODE = 2
MINOR_SEV_CODE = 3
WARNING_SEV_CODE = 4
INDETER_SEV_CODE = 5
CLEARED_SEV_CODE = 5
NORMAL_SEV_CODE = 5
OK_SEV_CODE = 5
INFORM_SEV_CODE = 6
DEBUG_SEV_CODE = 7
AUTH_SEV_CODE = 8
UNKNOWN_SEV_CODE = 9

# NOTE: The display text in single quotes can be changed depending on preference.
# eg. CRITICAL = 'critical' or CRITICAL = 'CRITICAL'

CRITICAL = 'critical'
MAJOR = 'major'
MINOR = 'minor'
WARNING = 'warning'
INDETERMINATE = 'indeterminate'
CLEARED = 'cleared'
NORMAL = 'normal'
OK = 'ok'
INFORM = 'informational'
DEBUG = 'debug'
AUTH = 'security'
UNKNOWN = 'unknown'
NOT_VALID = 'notValid'

ALL = [CRITICAL, MAJOR, MINOR, WARNING, INDETERMINATE, CLEARED, NORMAL, OK, INFORM, DEBUG, AUTH, UNKNOWN, NOT_VALID]

_SEVERITY_MAP = {
    CRITICAL: CRITICAL_SEV_CODE,
    MAJOR: MAJOR_SEV_CODE,
    MINOR: MINOR_SEV_CODE,
    WARNING: WARNING_SEV_CODE,
    INDETERMINATE: INDETER_SEV_CODE,
    CLEARED: CLEARED_SEV_CODE,
    NORMAL: NORMAL_SEV_CODE,
    OK: OK_SEV_CODE,
    INFORM: INFORM_SEV_CODE,
    DEBUG: DEBUG_SEV_CODE,
    AUTH: AUTH_SEV_CODE,
    UNKNOWN: UNKNOWN_SEV_CODE,
}

_DISPLAY_SEVERITY = {
    CRITICAL:      "Crit",
    MAJOR:         "Majr",
    MINOR:         "Minr",
    WARNING:       "Warn",
    INDETERMINATE: "Ind ",
    CLEARED:       "Clr",
    NORMAL:        "Norm",
    INFORM:        "Info",
    OK:            "Ok",
    DEBUG:         "Dbug",
    AUTH:          "Sec",
    UNKNOWN:       "Unkn"
}


class Helpers(object):

    @staticmethod
    def to_short_sev(severity):
        return _DISPLAY_SEVERITY.get(severity, _DISPLAY_SEVERITY['unknown'])

    @staticmethod
    def name_to_code(name):
        return _SEVERITY_MAP.get(name.lower(), UNKNOWN_SEV_CODE)
