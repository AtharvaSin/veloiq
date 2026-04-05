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
