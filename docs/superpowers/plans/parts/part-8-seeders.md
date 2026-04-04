## Part 8 — Data Seeders (Tasks 32-36)

> **Spec reference:** Section 6 (Data Seeder & Demo Reset) of `docs/superpowers/specs/2026-04-05-phase-a-foundation-design.md`

This part builds the deterministic synthetic-data seeder suite that powers `make demo-reset`. All randomness is seeded with `42` (via `settings.faker_seed`), so running the full pipeline twice produces byte-identical data. The 7 fuzzy-match test pairs from the spec are seeded verbatim into `cert_standard_links` so that Phase B's matching engine has a known ground truth to validate against.

**Dependency order (seed):** customers → standards → certificates + cert_standard_links → match_results → assessments → notifications → sales_escalations
**Truncate order (reverse of FK dependencies):** audit_log → sales_escalations → notifications → assessments → match_results → cert_standard_links → certificates → standards → customers

---

### Task 32: Faker providers for TIC domain

**Files:**
- Create: `backend/data_seeder/providers.py`
- Create: `backend/tests/data_seeder/__init__.py`
- Create: `backend/tests/data_seeder/test_providers.py`

- [ ] **Step 1: Write failing test for TIC providers**

Create `backend/tests/data_seeder/__init__.py` (empty).

Create `backend/tests/data_seeder/test_providers.py`:

```python
import random

from faker import Faker

from data_seeder.providers import TICProvider


def _make_faker() -> Faker:
    random.seed(42)
    Faker.seed(42)
    fake = Faker()
    fake.add_provider(TICProvider)
    return fake


def test_standard_code_returns_iso_iec_or_en_code() -> None:
    fake = _make_faker()
    code = fake.standard_code()
    assert any(code.startswith(p) for p in ("ISO ", "IEC ", "EN ", "ISO/IEC "))
    # "<prefix> <number>[:<year>]" shape
    assert len(code.split()) >= 2


def test_committee_name_returns_technical_committee_format() -> None:
    fake = _make_faker()
    committee = fake.committee_name()
    assert committee.startswith(("ISO/TC", "IEC/TC", "CEN/TC"))


def test_product_description_returns_tic_domain_text() -> None:
    fake = _make_faker()
    desc = fake.product_description()
    assert isinstance(desc, str)
    assert len(desc) > 10


def test_certificate_number_matches_tc_pattern() -> None:
    fake = _make_faker()
    cert_no = fake.certificate_number()
    assert cert_no.startswith("TC-")
    assert cert_no[3:].isdigit()


def test_tic_company_name_returns_industrial_style_name() -> None:
    fake = _make_faker()
    name = fake.tic_company_name()
    assert isinstance(name, str)
    assert len(name) > 3


def test_providers_are_deterministic_with_seed() -> None:
    fake1 = _make_faker()
    values1 = [fake1.standard_code() for _ in range(10)]

    fake2 = _make_faker()
    values2 = [fake2.standard_code() for _ in range(10)]

    assert values1 == values2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/data_seeder/test_providers.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'data_seeder.providers'`

- [ ] **Step 3: Create `backend/data_seeder/providers.py`**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/data_seeder/test_providers.py -v --no-cov
```

Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/data_seeder/providers.py backend/tests/data_seeder/__init__.py backend/tests/data_seeder/test_providers.py
git commit -m "feat(seeder): add TIC-domain Faker providers"
```

---

### Task 33: Customer + Standard seeders

**Files:**
- Create: `backend/data_seeder/seed_customers.py`, `backend/data_seeder/seed_standards.py`
- Create: `backend/tests/data_seeder/test_seed_customers.py`, `backend/tests/data_seeder/test_seed_standards.py`

- [ ] **Step 1: Write failing test for customer seeder**

Create `backend/tests/data_seeder/test_seed_customers.py`:

```python
import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.customer import Customer
from data_seeder.seed_customers import seed_customers


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_customers_creates_30_records(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    assert len(customers) == 30
    assert db_session.query(Customer).count() == 30


def test_seed_customers_country_distribution(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    counts = Counter(c.country for c in customers)
    assert counts["DE"] == 10
    assert counts["CN"] == 8
    assert counts["IN"] == 5
    assert counts["GB"] == 4
    assert counts["US"] == 3


def test_seed_customers_have_unique_customer_numbers(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    numbers = [c.customer_number for c in customers]
    assert len(numbers) == len(set(numbers))


def test_seed_customers_is_deterministic(db_session: Session) -> None:
    _seeded()
    first = [c.customer_number for c in seed_customers(db_session)]
    db_session.query(Customer).delete()
    db_session.flush()

    _seeded()
    second = [c.customer_number for c in seed_customers(db_session)]
    assert first == second
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/data_seeder/test_seed_customers.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'data_seeder.seed_customers'`

- [ ] **Step 3: Create `backend/data_seeder/seed_customers.py`**

```python
"""Seed 30 customers with fixed country distribution (10 DE, 8 CN, 5 IN, 4 GB, 3 US)."""
from faker import Faker
from sqlalchemy.orm import Session

from app.models.customer import Customer
from data_seeder.providers import TICProvider

COUNTRY_DISTRIBUTION: list[tuple[str, str, str, int]] = [
    # (country ISO2, sales_area, language, count)
    ("DE", "EMEA", "DE", 10),
    ("CN", "Greater China", "ZH", 8),
    ("IN", "South Asia", "EN", 5),
    ("GB", "EMEA", "EN", 4),
    ("US", "Americas", "EN", 3),
]


def seed_customers(db: Session) -> list[Customer]:
    """Insert 30 deterministic customers. Caller must flush or commit."""
    fake = Faker()
    fake.add_provider(TICProvider)

    customers: list[Customer] = []
    counter = 1
    for country, sales_area, language, count in COUNTRY_DISTRIBUTION:
        for _ in range(count):
            customer = Customer(
                customer_number=f"CUST-{counter:04d}",
                company_name=fake.tic_company_name(),
                country=country,
                sales_area=sales_area,
                language=language,
                contact_name=fake.name(),
                contact_email=fake.company_email(),
            )
            db.add(customer)
            customers.append(customer)
            counter += 1

    db.flush()
    return customers
```

- [ ] **Step 4: Run customer seeder test**

```bash
cd backend
pytest tests/data_seeder/test_seed_customers.py -v --no-cov
```

Expected: PASS (4 tests)

- [ ] **Step 5: Write failing test for standard seeder**

Create `backend/tests/data_seeder/test_seed_standards.py`:

```python
import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.standard import Standard
from data_seeder.seed_standards import seed_standards


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_standards_creates_50_records(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    assert len(standards) == 50
    assert db_session.query(Standard).count() == 50


def test_seed_standards_status_distribution(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    counts = Counter(s.status for s in standards)
    assert counts["00"] == 3
    assert counts["10"] + counts["20"] == 5
    assert counts["30"] == 5
    assert counts["40"] == 5
    assert counts["50"] == 5
    assert counts["60"] == 15
    assert counts["90"] == 7
    assert counts["95"] == 5


def test_seed_standards_includes_fuzzy_match_anchors(db_session: Session) -> None:
    """The 7 Natos sides of the fuzzy test pairs must be seeded as standards."""
    _seeded()
    seed_standards(db_session)
    codes = {s.ac_code for s in db_session.query(Standard).all()}
    expected_anchors = {
        "ISO 9001:2015",
        "ISO 14001:2015",
        "IEC 62368-1:2023",
        "ISO 1234:1998",
        "ISO 14001",
        "ISO 45001:2018",
        "IEC 61000-4-2:2008",
    }
    assert expected_anchors.issubset(codes)


def test_seed_standards_ac_codes_unique(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    codes = [s.ac_code for s in standards]
    assert len(codes) == len(set(codes))
```

- [ ] **Step 6: Create `backend/data_seeder/seed_standards.py`**

```python
"""Seed 50 standards across ISO stages including 7 fuzzy-match anchor codes."""
from datetime import datetime, timezone

from faker import Faker
from sqlalchemy.orm import Session

from app.models.standard import Standard
from data_seeder.providers import TICProvider

# (status, count) — totals to 50
STATUS_DISTRIBUTION: list[tuple[str, int]] = [
    ("00", 3),
    ("10", 3),
    ("20", 2),
    ("30", 5),
    ("40", 5),
    ("50", 5),
    ("60", 15),
    ("90", 7),
    ("95", 5),
]

# 7 anchor codes that pair with messy SAP refs in Task 34 (fuzzy-match test pairs)
FUZZY_MATCH_ANCHORS: list[tuple[str, str, str, str, int | None]] = [
    # (ac_code, title, base_number, normalized_code, version_year)
    ("ISO 9001:2015", "Quality management systems — Requirements", "9001", "iso 9001:2015", 2015),
    ("ISO 14001:2015", "Environmental management systems — Requirements", "14001", "iso 14001:2015", 2015),
    ("IEC 62368-1:2023", "Audio/video, information and communication technology equipment — Safety", "62368", "iec 62368-1:2023", 2023),
    ("ISO 1234:1998", "Gear tooth modifications", "1234", "iso 1234:1998", 1998),
    ("ISO 14001", "Environmental management systems", "14001", "iso 14001", None),
    ("ISO 45001:2018", "Occupational health and safety management systems", "45001", "iso 45001:2018", 2018),
    ("IEC 61000-4-2:2008", "Electromagnetic compatibility — ESD immunity test", "61000", "iec 61000-4-2:2008", 2008),
]


def _parse_version_year(ac_code: str) -> int | None:
    if ":" in ac_code:
        tail = ac_code.rsplit(":", 1)[1]
        if tail.isdigit():
            return int(tail)
    return None


def seed_standards(db: Session) -> list[Standard]:
    """Insert 50 deterministic standards. Includes 7 fuzzy-match anchor codes."""
    fake = Faker()
    fake.add_provider(TICProvider)
    now = datetime.now(timezone.utc)

    standards: list[Standard] = []
    used_codes: set[str] = set()

    # Pre-seed the 7 fuzzy anchors with status="60" (active, most common bucket)
    for ac_code, title, base_number, normalized_code, version_year in FUZZY_MATCH_ANCHORS:
        standard = Standard(
            ac_code=ac_code,
            title=title,
            status="60",
            normalized_code=normalized_code,
            base_number=base_number,
            version_year=version_year,
            committee=fake.committee_name(),
            ics_code=fake.ics_code(),
            source_payload={"source": "fuzzy_anchor", "raw": ac_code},
            ingested_at=now,
        )
        db.add(standard)
        standards.append(standard)
        used_codes.add(ac_code)

    # Distribution tracker: how many of each status we still need.
    remaining: dict[str, int] = dict(STATUS_DISTRIBUTION)
    # Anchors consumed 7 "60" slots already
    remaining["60"] = max(0, remaining["60"] - 7)

    # Fill remainder
    for status, count in remaining.items():
        for _ in range(count):
            while True:
                ac_code = fake.standard_code()
                if ac_code not in used_codes:
                    used_codes.add(ac_code)
                    break
            base_number = ac_code.split()[1].split(":")[0].split("-")[0]
            version_year = _parse_version_year(ac_code)
            standard = Standard(
                ac_code=ac_code,
                title=fake.sentence(nb_words=8).rstrip("."),
                status=status,
                normalized_code=ac_code.lower(),
                base_number=base_number,
                version_year=version_year,
                committee=fake.committee_name(),
                ics_code=fake.ics_code(),
                source_payload={"source": "synthetic", "raw": ac_code},
                ingested_at=now,
            )
            db.add(standard)
            standards.append(standard)

    db.flush()
    return standards
```

- [ ] **Step 7: Run standard seeder test**

```bash
cd backend
pytest tests/data_seeder/test_seed_standards.py -v --no-cov
```

Expected: PASS (4 tests)

- [ ] **Step 8: Commit**

```bash
git add backend/data_seeder/seed_customers.py backend/data_seeder/seed_standards.py backend/tests/data_seeder/test_seed_customers.py backend/tests/data_seeder/test_seed_standards.py
git commit -m "feat(seeder): add customer and standard seeders with fuzzy-match anchors"
```

---

### Task 34: Certificate + CertStandardLink seeder (with fuzzy test pairs)

**Files:**
- Create: `backend/data_seeder/seed_certificates.py`
- Create: `backend/tests/data_seeder/test_seed_certificates.py`

This seeder creates 200 certificates distributed 1-10 per customer, then adds ~400 cert_standard_links. Critically, it seeds the **7 fuzzy-match SAP-side refs** verbatim so Phase B has a deterministic test set.

- [ ] **Step 1: Write failing test for certificate + link seeder**

Create `backend/tests/data_seeder/test_seed_certificates.py`:

```python
import random

from faker import Faker
from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from data_seeder.seed_certificates import FUZZY_MATCH_SAP_REFS, seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_standards import seed_standards


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_certificates_creates_200_records(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, links = seed_certificates_and_links(db_session, customers, standards)

    assert len(certs) == 200
    assert db_session.query(Certificate).count() == 200


def test_seed_certificates_distributed_across_customers(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, _ = seed_certificates_and_links(db_session, customers, standards)

    # Every certificate should reference an existing customer
    customer_ids = {c.id for c in customers}
    assert all(cert.customer_id in customer_ids for cert in certs)

    # No customer has more than 10 certificates, none has zero
    from collections import Counter
    counts = Counter(cert.customer_id for cert in certs)
    assert max(counts.values()) <= 10
    assert min(counts.values()) >= 1


def test_seed_cert_links_count_around_400(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    _, links = seed_certificates_and_links(db_session, customers, standards)

    assert 380 <= len(links) <= 420  # ~2 per cert ± noise
    assert db_session.query(CertStandardLink).count() == len(links)


def test_fuzzy_match_sap_refs_present(db_session: Session) -> None:
    """All 7 messy SAP-format refs must be present in cert_standard_links."""
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    seed_certificates_and_links(db_session, customers, standards)

    stored_refs = {link.standard_ref for link in db_session.query(CertStandardLink).all()}
    expected_sap_refs = {pair[1] for pair in FUZZY_MATCH_SAP_REFS}
    assert expected_sap_refs.issubset(stored_refs)


def test_certificate_statuses_all_valid(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, _ = seed_certificates_and_links(db_session, customers, standards)

    valid_statuses = {"active", "expiring", "expired", "suspended"}
    assert all(c.status in valid_statuses for c in certs)
```

- [ ] **Step 2: Create `backend/data_seeder/seed_certificates.py`**

```python
"""Seed 200 certificates + ~400 cert_standard_links including 7 fuzzy-match test pairs."""
import random
from datetime import date, datetime, timedelta, timezone

from faker import Faker
from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.standard import Standard
from data_seeder.providers import TICProvider

# 7 fuzzy-match test pairs: (anchor_ac_code, messy_sap_ref, normalized_ref, base_number)
FUZZY_MATCH_SAP_REFS: list[tuple[str, str, str, str]] = [
    ("ISO 9001:2015", "DIN EN ISO 9001:2015-11", "9001:2015", "9001"),
    ("ISO 14001:2015", "BS EN ISO 14001:2015", "14001:2015", "14001"),
    ("IEC 62368-1:2023", "EN IEC 62368-1:2023/AC:2024", "62368-1:2023", "62368"),
    ("ISO 1234:1998", "ANSI ABC 331:1999/ISO 1234:1998", "1234:1998", "1234"),
    ("ISO 14001", "ISO 1401", "1401", "1401"),
    ("ISO 45001:2018", "GB/T 45001-2020", "45001:2020", "45001"),
    ("IEC 61000-4-2:2008", "DIN EN 61000-4-2 VDE 0847-4-2:2010-04", "61000-4-2:2010", "61000"),
]

CERT_STATUSES: list[tuple[str, float]] = [
    ("active", 0.65),
    ("expiring", 0.15),
    ("expired", 0.15),
    ("suspended", 0.05),
]


def _choose_status() -> str:
    r = random.random()
    cumulative = 0.0
    for status, weight in CERT_STATUSES:
        cumulative += weight
        if r <= cumulative:
            return status
    return "active"


def _distribute_certs_across_customers(num_customers: int, total_certs: int) -> list[int]:
    """Return list of length num_customers where each entry is 1-10 and sum == total_certs."""
    # Start with 1 per customer (ensures min=1)
    counts = [1] * num_customers
    remaining = total_certs - num_customers

    while remaining > 0:
        idx = random.randrange(num_customers)
        if counts[idx] < 10:
            counts[idx] += 1
            remaining -= 1
    return counts


def seed_certificates_and_links(
    db: Session,
    customers: list[Customer],
    standards: list[Standard],
) -> tuple[list[Certificate], list[CertStandardLink]]:
    """Insert 200 certs + ~400 links. Includes 7 fuzzy-match SAP-format test pairs."""
    fake = Faker()
    fake.add_provider(TICProvider)
    now = datetime.now(timezone.utc)
    today = date.today()

    certs_per_customer = _distribute_certs_across_customers(len(customers), 200)

    certificates: list[Certificate] = []
    cert_counter = 1
    for customer, cert_count in zip(customers, certs_per_customer, strict=True):
        for _ in range(cert_count):
            status = _choose_status()
            # Issue date 0-5 years ago
            issue_offset_days = random.randint(0, 5 * 365)
            issue_date = today - timedelta(days=issue_offset_days)
            # Certificates are 3-year cycles typically
            expiry_date = issue_date + timedelta(days=3 * 365)

            cert = Certificate(
                certificate_number=f"TC-{40000 + cert_counter:05d}",
                customer_id=customer.id,
                product_description=fake.product_description(),
                status=status,
                issue_date=issue_date,
                expiry_date=expiry_date,
            )
            db.add(cert)
            certificates.append(cert)
            cert_counter += 1

    db.flush()

    # --- Links: ~2 per certificate, plus embed the 7 fuzzy pairs ---
    links: list[CertStandardLink] = []

    # 1) Embed 7 fuzzy-match SAP refs onto the first 7 certificates
    for idx, (_, sap_ref, normalized_ref, base_number) in enumerate(FUZZY_MATCH_SAP_REFS):
        link = CertStandardLink(
            certificate_id=certificates[idx].id,
            standard_ref=sap_ref,
            normalized_ref=normalized_ref,
            base_number=base_number,
            linked_at=now,
        )
        db.add(link)
        links.append(link)

    # 2) For every certificate, add 1-3 synthetic links (~2 avg)
    for cert in certificates:
        num_links = random.choices([1, 2, 3], weights=[0.25, 0.5, 0.25], k=1)[0]
        chosen = random.sample(standards, k=min(num_links, len(standards)))
        for std in chosen:
            link = CertStandardLink(
                certificate_id=cert.id,
                standard_ref=std.ac_code,
                normalized_ref=std.normalized_code,
                base_number=std.base_number,
                linked_at=now,
            )
            db.add(link)
            links.append(link)

    db.flush()
    return certificates, links
```

- [ ] **Step 3: Run certificate seeder test**

```bash
cd backend
pytest tests/data_seeder/test_seed_certificates.py -v --no-cov
```

Expected: PASS (5 tests)

- [ ] **Step 4: Commit**

```bash
git add backend/data_seeder/seed_certificates.py backend/tests/data_seeder/test_seed_certificates.py
git commit -m "feat(seeder): add certificate + cert_standard_link seeder with 7 fuzzy test pairs"
```

---

### Task 35: Historical data seeder (matches, assessments, notifications, escalations)

**Files:**
- Create: `backend/data_seeder/seed_historical.py`
- Create: `backend/tests/data_seeder/test_seed_historical.py`

This seeder creates the historical demo context: 30 match_results, 30 assessments, 20 notifications, 5 sales_escalations. These records give Phase B-D workflows a realistic starting state.

- [ ] **Step 1: Write failing test for historical seeder**

Create `backend/tests/data_seeder/test_seed_historical.py`:

```python
import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from data_seeder.seed_certificates import seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_historical import seed_historical
from data_seeder.seed_standards import seed_standards


def _bootstrap(db_session: Session):
    random.seed(42)
    Faker.seed(42)
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    _, links = seed_certificates_and_links(db_session, customers, standards)
    return standards, links, customers


def test_seed_historical_creates_30_matches(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    assert len(matches) == 30
    assert db_session.query(MatchResult).count() == 30


def test_match_confidence_tier_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(m.confidence_tier for m in matches)
    assert counts["auto_match"] == 10
    assert counts["expert_review"] == 15
    assert counts["manual_triage"] == 5


def test_match_similarity_scores_match_tier_bands(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    for m in matches:
        score = float(m.similarity_score)
        if m.confidence_tier == "auto_match":
            assert score > 0.95
        elif m.confidence_tier == "expert_review":
            assert 0.70 <= score <= 0.95
        elif m.confidence_tier == "manual_triage":
            assert score < 0.70


def test_seed_historical_creates_30_assessments(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    assert len(assessments) == 30
    assert db_session.query(Assessment).count() == 30


def test_assessment_impact_classification_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(a.impact_classification for a in assessments)
    assert counts["no_change"] == 10
    assert counts["minor_technical"] == 10
    assert counts["major_technical"] == 5
    assert counts["safety_critical"] == 5


def test_seed_historical_creates_20_notifications(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, _ = seed_historical(db_session, standards, links, customers)
    assert len(notifications) == 20
    assert db_session.query(Notification).count() == 20


def test_seed_historical_creates_5_escalations_for_breached(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, escalations = seed_historical(db_session, standards, links, customers)
    assert len(escalations) == 5
    breached_ids = {n.id for n in notifications if n.status == "breached"}
    assert {e.notification_id for e in escalations} == breached_ids


def test_historical_seeder_referential_integrity(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, assessments, notifications, escalations = seed_historical(
        db_session, standards, links, customers
    )
    match_ids = {m.id for m in matches}
    for a in assessments:
        assert a.match_result_id in match_ids
    assessment_ids = {a.id for a in assessments}
    for n in notifications:
        assert n.assessment_id in assessment_ids
    notification_ids = {n.id for n in notifications}
    for e in escalations:
        assert e.notification_id in notification_ids
```

- [ ] **Step 2: Create `backend/data_seeder/seed_historical.py`**

```python
"""Seed 30 match_results + 30 assessments + 20 notifications + 5 sales_escalations."""
import hashlib
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from faker import Faker
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard

MATCH_TIER_DISTRIBUTION: list[tuple[str, int, tuple[float, float]]] = [
    # (confidence_tier, count, (score_min, score_max))
    ("auto_match", 10, (0.951, 0.999)),
    ("expert_review", 15, (0.700, 0.950)),
    ("manual_triage", 5, (0.400, 0.699)),
]

ASSESSMENT_IMPACT_DISTRIBUTION: list[tuple[str, int]] = [
    ("no_change", 10),
    ("minor_technical", 10),
    ("major_technical", 5),
    ("safety_critical", 5),
]

IMPACT_TO_ACTION: dict[str, str] = {
    "no_change": "reconfirm",
    "administrative": "reconfirm",
    "minor_technical": "reconfirm",
    "major_technical": "retest",
    "safety_critical": "suspend",
}

NOTIFICATION_STATUS_MIX: list[tuple[str, int]] = [
    # Total = 20; 5 breached drives the 5 escalations
    ("sent", 3),
    ("delivered", 3),
    ("opened", 4),
    ("clicked", 5),
    ("breached", 5),
]

ASSESSORS = (
    "Dr. M. Weber", "Dr. S. Chen", "Dr. R. Kumar", "Dr. A. Müller", "Dr. L. Schmidt",
)


def _round(value: float) -> Decimal:
    return Decimal(f"{value:.3f}")


def seed_historical(
    db: Session,
    standards: list[Standard],
    cert_links: list[CertStandardLink],
    customers: list[Customer],
) -> tuple[list[MatchResult], list[Assessment], list[Notification], list[SalesEscalation]]:
    """Seed historical match_results, assessments, notifications, sales_escalations."""
    fake = Faker()
    now = datetime.now(timezone.utc)

    # --- 30 match_results ---
    matches: list[MatchResult] = []
    used_pairs: set[tuple] = set()
    link_pool = list(cert_links)
    random.shuffle(link_pool)
    link_idx = 0

    for tier, count, (score_min, score_max) in MATCH_TIER_DISTRIBUTION:
        for _ in range(count):
            # Pick a unique (standard, link) pair
            while True:
                std = random.choice(standards)
                link = link_pool[link_idx % len(link_pool)]
                link_idx += 1
                pair = (std.id, link.id)
                if pair not in used_pairs:
                    used_pairs.add(pair)
                    break

            score = random.uniform(score_min, score_max)
            lev = random.uniform(score_min - 0.05, min(score_max + 0.02, 1.0))
            jw = random.uniform(score_min - 0.03, min(score_max + 0.03, 1.0))
            ts = random.uniform(score_min - 0.04, min(score_max + 0.02, 1.0))

            status = "reviewed" if tier != "manual_triage" else "pending"
            reviewed_at = now - timedelta(days=random.randint(1, 60)) if status == "reviewed" else None
            matched_at = (reviewed_at or now) - timedelta(hours=random.randint(1, 72))

            match = MatchResult(
                natos_standard_id=std.id,
                cert_link_id=link.id,
                similarity_score=_round(max(0.0, min(1.0, score))),
                levenshtein_score=_round(max(0.0, min(1.0, lev))),
                jaro_winkler_score=_round(max(0.0, min(1.0, jw))),
                token_set_score=_round(max(0.0, min(1.0, ts))),
                confidence_tier=tier,
                status=status,
                matched_at=matched_at,
                reviewed_at=reviewed_at,
            )
            db.add(match)
            matches.append(match)

    db.flush()

    # --- 30 assessments (one per match) ---
    assessments: list[Assessment] = []
    match_pool = list(matches)
    random.shuffle(match_pool)
    match_idx = 0

    for impact, count in ASSESSMENT_IMPACT_DISTRIBUTION:
        for _ in range(count):
            match = match_pool[match_idx]
            match_idx += 1

            action = IMPACT_TO_ACTION[impact]
            decision = "approved" if impact != "safety_critical" else "escalated"
            decided_at = now - timedelta(days=random.randint(1, 45))
            assessor = random.choice(ASSESSORS)

            sig_input = f"{match.id}:{assessor}:{decided_at.isoformat()}".encode()
            signature = hashlib.sha256(sig_input).hexdigest()

            assessment = Assessment(
                match_result_id=match.id,
                assessor_id=assessor,
                impact_classification=impact,
                action_required=action,
                reason_code=f"RC-{impact.upper()}-{random.randint(100, 999)}",
                notes=fake.sentence(nb_words=12),
                decision=decision,
                decided_at=decided_at,
                signature_hash=signature,
            )
            db.add(assessment)
            assessments.append(assessment)

    db.flush()

    # --- 20 notifications (pick first 20 assessments; assign customers via match→link→cert) ---
    from app.models.certificate import Certificate  # local import to avoid cycle

    notifications: list[Notification] = []
    link_by_id = {link.id: link for link in cert_links}
    cert_id_to_customer: dict = {}
    cert_ids = {link.certificate_id for link in cert_links}
    for cert in db.query(Certificate).filter(Certificate.id.in_(cert_ids)).all():
        cert_id_to_customer[cert.id] = cert.customer_id
    customer_lang = {c.id: c.language for c in customers}

    expanded_statuses: list[str] = []
    for status, count in NOTIFICATION_STATUS_MIX:
        expanded_statuses.extend([status] * count)

    for idx in range(20):
        assessment = assessments[idx]
        match = next(m for m in matches if m.id == assessment.match_result_id)
        link = link_by_id[match.cert_link_id]
        customer_id = cert_id_to_customer[link.certificate_id]
        language = customer_lang.get(customer_id, "EN")

        status = expanded_statuses[idx]
        sent_at = now - timedelta(days=random.randint(5, 30))
        delivered_at = sent_at + timedelta(minutes=random.randint(1, 30)) if status in {"delivered", "opened", "clicked", "breached"} else None
        opened_at = (delivered_at + timedelta(hours=random.randint(1, 48))) if status in {"opened", "clicked"} and delivered_at else None
        clicked_at = (opened_at + timedelta(minutes=random.randint(1, 120))) if status == "clicked" and opened_at else None
        sla_deadline = sent_at + timedelta(days=14)

        notification = Notification(
            assessment_id=assessment.id,
            customer_id=customer_id,
            template_language=language,
            subject=f"Certificate action required: {assessment.action_required}",
            body_html=f"<p>{fake.paragraph(nb_sentences=3)}</p>",
            status=status,
            sent_at=sent_at,
            delivered_at=delivered_at,
            opened_at=opened_at,
            clicked_at=clicked_at,
            sla_deadline=sla_deadline,
        )
        db.add(notification)
        notifications.append(notification)

    db.flush()

    # --- 5 sales_escalations (one per breached notification) ---
    escalations: list[SalesEscalation] = []
    for notification in notifications:
        if notification.status != "breached":
            continue
        escalation = SalesEscalation(
            notification_id=notification.id,
            customer_id=notification.customer_id,
            escalation_reason="sla_breach",
            opportunity_value=Decimal(f"{random.randint(5_000, 150_000)}.00"),
            assigned_to=fake.name(),
            status=random.choice(["open", "contacted"]),
            created_at=notification.sla_deadline + timedelta(hours=1),
            resolved_at=None,
        )
        db.add(escalation)
        escalations.append(escalation)

    db.flush()
    return matches, assessments, notifications, escalations
```

- [ ] **Step 3: Run historical seeder tests**

```bash
cd backend
pytest tests/data_seeder/test_seed_historical.py -v --no-cov
```

Expected: PASS (8 tests)

- [ ] **Step 4: Commit**

```bash
git add backend/data_seeder/seed_historical.py backend/tests/data_seeder/test_seed_historical.py
git commit -m "feat(seeder): add historical matches/assessments/notifications/escalations seeder"
```

---

### Task 36: `seed_all.py` orchestrator with TRUNCATE + verification

**Files:**
- Create: `backend/data_seeder/seed_all.py`
- Create: `backend/tests/data_seeder/test_seed_all.py`

This is the one-command entry point invoked by `make demo-reset`. It TRUNCATEs in reverse FK order, reseeds deterministically, and prints a summary. A final idempotency test verifies that two full runs produce identical UUIDs.

- [ ] **Step 1: Write failing test for orchestrator**

Create `backend/tests/data_seeder/test_seed_all.py`:

```python
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.audit_log import AuditLog
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard
from data_seeder.seed_all import run_seed_pipeline


def test_orchestrator_seeds_expected_counts(db_session: Session) -> None:
    run_seed_pipeline(db_session)

    assert db_session.query(Customer).count() == 30
    assert db_session.query(Standard).count() == 50
    assert db_session.query(Certificate).count() == 200
    assert 380 <= db_session.query(CertStandardLink).count() <= 420
    assert db_session.query(MatchResult).count() == 30
    assert db_session.query(Assessment).count() == 30
    assert db_session.query(Notification).count() == 20
    assert db_session.query(SalesEscalation).count() == 5


def test_orchestrator_is_deterministic_across_runs(db_session: Session) -> None:
    """Two runs of the pipeline produce IDENTICAL data (counts + sample UUIDs)."""
    run_seed_pipeline(db_session)
    first_customer_ids = [
        c.id for c in db_session.query(Customer).order_by(Customer.customer_number).all()
    ]
    first_standard_codes = [
        s.ac_code for s in db_session.query(Standard).order_by(Standard.ac_code).all()
    ]

    # Clear everything, re-run
    for model in (
        AuditLog, SalesEscalation, Notification, Assessment, MatchResult,
        CertStandardLink, Certificate, Standard, Customer,
    ):
        db_session.query(model).delete()
    db_session.flush()

    run_seed_pipeline(db_session)
    second_customer_ids = [
        c.id for c in db_session.query(Customer).order_by(Customer.customer_number).all()
    ]
    second_standard_codes = [
        s.ac_code for s in db_session.query(Standard).order_by(Standard.ac_code).all()
    ]

    assert first_customer_ids == second_customer_ids
    assert first_standard_codes == second_standard_codes
```

- [ ] **Step 2: Create `backend/data_seeder/seed_all.py`**

```python
"""Orchestrator: TRUNCATE all tables (reverse FK order) then reseed deterministically.

Entry point for `make demo-reset`. Running this twice MUST produce identical data.
"""
import random

from faker import Faker
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, engine
from data_seeder.seed_certificates import seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_historical import seed_historical
from data_seeder.seed_standards import seed_standards

TRUNCATE_SQL = text(
    "TRUNCATE audit_log, sales_escalations, notifications, assessments, "
    "match_results, cert_standard_links, certificates, standards, customers "
    "RESTART IDENTITY CASCADE"
)


def _reset_seeds() -> None:
    """Reset both `random` and `Faker` to the configured fixed seed."""
    random.seed(settings.faker_seed)
    Faker.seed(settings.faker_seed)


def run_seed_pipeline(db: Session) -> dict[str, int]:
    """Reset seeds and execute all seeders in dependency order. Returns summary counts.

    Caller is responsible for commit/rollback. Used by both the CLI entry point
    and the test suite.
    """
    _reset_seeds()

    customers = seed_customers(db)
    standards = seed_standards(db)
    certificates, cert_links = seed_certificates_and_links(db, customers, standards)
    matches, assessments, notifications, escalations = seed_historical(
        db, standards, cert_links, customers
    )

    return {
        "customers": len(customers),
        "standards": len(standards),
        "certificates": len(certificates),
        "cert_standard_links": len(cert_links),
        "match_results": len(matches),
        "assessments": len(assessments),
        "notifications": len(notifications),
        "sales_escalations": len(escalations),
    }


def reset_and_seed() -> None:
    """CLI entry point: TRUNCATE all tables, then run full seeder pipeline."""
    # 1. Truncate in a fresh connection (outside the Session)
    with engine.connect() as conn:
        conn.execute(TRUNCATE_SQL)
        conn.commit()

    # 2. Re-seed inside a Session and commit
    with SessionLocal() as db:
        counts = run_seed_pipeline(db)
        db.commit()

    summary = ", ".join(f"{v} {k}" for k, v in counts.items())
    print(f"Seeded: {summary}")


if __name__ == "__main__":
    reset_and_seed()
```

- [ ] **Step 3: Run orchestrator test**

```bash
cd backend
pytest tests/data_seeder/test_seed_all.py -v --no-cov
```

Expected: PASS (2 tests)

- [ ] **Step 4: Run full seeder suite**

```bash
cd backend
pytest tests/data_seeder/ -v --no-cov
```

Expected: PASS (all tests from Tasks 32-36)

- [ ] **Step 5: Execute `make demo-reset` against dev DB**

```bash
cd backend
source .venv/Scripts/activate  # Windows Git Bash
make demo-reset
```

Expected output:
```
Seeded: 30 customers, 50 standards, 200 certificates, 400 cert_standard_links, 30 match_results, 30 assessments, 20 notifications, 5 sales_escalations
```

(Actual `cert_standard_links` count varies 380-420 due to weighted random fan-out.)

- [ ] **Step 6: Verify idempotency via running demo-reset twice**

```bash
cd backend
make demo-reset
make demo-reset
psql "$DATABASE_URL" -c "SELECT count(*) FROM customers;"
psql "$DATABASE_URL" -c "SELECT customer_number, id FROM customers ORDER BY customer_number LIMIT 3;"
```

Record the first UUID. Run `make demo-reset` once more and re-query — the UUIDs must be identical.

- [ ] **Step 7: Commit**

```bash
git add backend/data_seeder/seed_all.py backend/tests/data_seeder/test_seed_all.py
git commit -m "feat(seeder): add seed_all orchestrator with TRUNCATE + determinism test"
```

---

## Part 8 Verification

Part 8 is complete when **all** of the following are true:

1. **Faker providers:** `backend/data_seeder/providers.py` exposes `TICProvider` with `standard_code`, `committee_name`, `product_description`, `certificate_number`, `tic_company_name`, `ics_code`. All provider tests pass.
2. **Customer seeder:** Produces exactly 30 customers with distribution 10 DE / 8 CN / 5 IN / 4 GB / 3 US. Customer numbers are unique `CUST-0001`..`CUST-0030`.
3. **Standard seeder:** Produces exactly 50 standards matching the ISO-stage distribution (3/5/5/5/5/15/7/5). The 7 fuzzy-match anchor codes (`ISO 9001:2015`, `ISO 14001:2015`, `IEC 62368-1:2023`, `ISO 1234:1998`, `ISO 14001`, `ISO 45001:2018`, `IEC 61000-4-2:2008`) are present verbatim.
4. **Certificate seeder:** Produces exactly 200 certificates distributed 1-10 per customer and ~400 `cert_standard_links` (weighted 1-3 per cert). All 7 messy SAP-format refs from the spec table are stored verbatim in `cert_standard_links.standard_ref`.
5. **Historical seeder:** Produces 30 matches (10 auto / 15 expert / 5 triage with matching similarity bands), 30 assessments (10 no_change / 10 minor_technical / 5 major_technical / 5 safety_critical), 20 notifications (status mix spanning sent → breached), 5 escalations (one per breached notification). Full referential integrity across matches → assessments → notifications → escalations.
6. **Orchestrator:** `python -m data_seeder.seed_all` TRUNCATEs all 9 tables (reverse FK order) and reseeds cleanly. Prints summary line.
7. **Determinism:** Running the pipeline twice produces identical `customer_number`-ordered UUID lists and identical sorted `ac_code` lists. Verified by `test_orchestrator_is_deterministic_across_runs`.
8. **All tests pass:** `pytest tests/data_seeder/ -v` shows all tests green (≥25 tests across Tasks 32-36). Overall suite still meets the 85% coverage floor.
9. **Makefile command works:** `make demo-reset` runs end-to-end in <5 seconds against the dev Postgres and produces the expected console summary.
