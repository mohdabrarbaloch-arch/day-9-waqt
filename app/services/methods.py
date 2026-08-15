"""Prayer-time calculation methods (ISO/IEEE-style presets used across the
Muslim world). Angles are in degrees; asr factor is the shadow-length juristic
rule (1 = Shafi/Maliki/Hanbali, 2 = Hanafi)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CalculationMethod:
    id: int
    name: str
    fajr_angle: float
    isha_angle: float
    isha_interval: int | None  # minutes after Maghrib when set (overrides angle)
    asr_factor: float  # 1 or 2
    region: str


METHODS: dict[int, CalculationMethod] = {
    1: CalculationMethod(1, "University of Karachi", 18.0, 18.0, None, 1, "PK/IN"),
    2: CalculationMethod(
        2, "ISNA (Islamic Society of North America)", 15.0, 15.0, None, 1, "US/CA"
    ),
    3: CalculationMethod(
        3, "MWL (Muslim World League)", 18.0, 17.0, None, 1, "EU/Global"
    ),
    4: CalculationMethod(4, "Umm Al-Qura, Makkah", 18.5, 0.0, 90, 1, "SA"),
    5: CalculationMethod(5, "Egyptian General Authority", 19.5, 17.5, None, 1, "EG"),
    6: CalculationMethod(6, "Tehran", 17.7, 14.0, None, 1, "IR"),
    7: CalculationMethod(
        7, "Jafari (Shia Ithna-Ashari)", 16.0, 14.0, None, 1, "IR/Global"
    ),
    8: CalculationMethod(8, "Gulf Region", 19.5, 0.0, 90, 1, "GCC"),
    9: CalculationMethod(9, "Kuwait", 18.0, 17.5, None, 1, "KW"),
    10: CalculationMethod(10, "Qatar", 18.0, 0.0, 90, 1, "QA"),
    11: CalculationMethod(11, "Singapore", 20.0, 18.0, None, 1, "SG"),
    12: CalculationMethod(12, "Turkey (Diyanet)", 18.0, 17.0, None, 1, "TR"),
    13: CalculationMethod(13, "Dubai (DUBIA)", 18.2, 18.2, None, 1, "AE"),
    14: CalculationMethod(14, "Morocco", 19.0, 17.0, None, 1, "MA"),
    15: CalculationMethod(15, "Pakistan (Faisalabad)", 18.0, 18.0, None, 2, "PK"),
    16: CalculationMethod(16, "Custom", 18.0, 17.0, None, 1, "Global"),
}

DEFAULT_METHOD_ID = 1  # University of Karachi — the default for Pakistan


def get_method(method_id: int) -> CalculationMethod:
    return METHODS.get(method_id, METHODS[DEFAULT_METHOD_ID])
