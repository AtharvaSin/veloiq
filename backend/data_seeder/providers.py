"""Custom Faker providers for TIC (Testing/Inspection/Certification) domain data."""
from faker.providers import BaseProvider


class TICProvider(BaseProvider):
    """Faker provider producing realistic TIC-industry synthetic values."""

    _STANDARD_PREFIXES = ("ISO ", "IEC ", "ISO/IEC ", "EN ")
    _COMMITTEE_ROOTS = ("ISO/TC", "IEC/TC", "CEN/TC")
    _PRODUCT_CATEGORIES = (
        "Industrial Control Panel",
        "LED Lighting Module",
        "Medical Infusion Pump",
        "Automotive ECU",
        "Household Refrigerator",
        "Power Converter",
        "Safety Relay",
        "Surge Protection Device",
        "Photovoltaic Inverter",
        "Electric Motor Drive",
        "Switchgear Assembly",
        "Smart Meter",
        "HVAC Controller",
        "Emergency Lighting Unit",
        "UPS System",
        "Battery Management System",
    )
    _COMPANY_SUFFIXES = (
        "Technologies Co., Ltd.",
        "Industries GmbH",
        "Electric Ltd.",
        "Systems AG",
        "Manufacturing Pvt. Ltd.",
        "Automation Inc.",
        "Power Solutions Corp.",
        "Engineering Works",
    )
    _COMPANY_ROOTS = (
        "Siemens", "Bosch", "ABB", "Schneider", "Huawei", "Hitachi",
        "Mitsubishi", "Honeywell", "Emerson", "Rockwell", "Yokogawa",
        "Delta", "Omron", "Panasonic", "Danfoss", "Fuji", "Tata",
        "Mahindra", "Larsen", "Reliance", "Wipro",
    )

    def standard_code(self) -> str:
        """Return a synthetic standard code like 'ISO 9001:2015' or 'IEC 61010-1:2010'."""
        prefix = self.random_element(self._STANDARD_PREFIXES)
        number = self.random_int(min=1000, max=99999)
        part = self.random_element((None, None, None, 1, 2, 3, 4))
        year = self.random_int(min=1998, max=2024)
        base = f"{number}-{part}" if part else str(number)
        return f"{prefix}{base}:{year}"

    def committee_name(self) -> str:
        """Return a technical committee designation like 'ISO/TC 176'."""
        root = self.random_element(self._COMMITTEE_ROOTS)
        number = self.random_int(min=1, max=350)
        return f"{root} {number}"

    def product_description(self) -> str:
        """Return a TIC-domain product description with modifiers."""
        category = self.random_element(self._PRODUCT_CATEGORIES)
        rating = self.random_element(("24V DC", "230V AC", "400V AC", "48V DC", "12V DC"))
        current = self.random_int(min=1, max=63)
        return f"{category} — {rating}, {current}A, IP54 enclosure"

    def certificate_number(self) -> str:
        """Return a TÜV-style certificate number like 'TC-44210'."""
        return f"TC-{self.random_int(min=10000, max=99999)}"

    def tic_company_name(self) -> str:
        """Return a synthetic industrial/TIC customer company name."""
        root = self.random_element(self._COMPANY_ROOTS)
        suffix = self.random_element(self._COMPANY_SUFFIXES)
        return f"{root} {suffix}"

    def ics_code(self) -> str:
        """Return an ICS (International Classification for Standards) code like '29.130.20'."""
        group = self.random_int(min=1, max=99)
        sub = self.random_int(min=0, max=200)
        item = self.random_int(min=0, max=99)
        return f"{group:02d}.{sub:03d}.{item:02d}"
