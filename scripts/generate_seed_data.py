from faker import Faker
import random
from datetime import date, timedelta


fake = Faker("en_GB")


PROPERTY_TYPES = ["Flat", "House", "Maisonette", "Bungalow"]
COMPLIANCE_STATUSES = ["Compliant", "Inspection Due", "Non-Compliant"]
CONTRACTOR_SPECIALISMS = [
    "Boiler Repair",
    "Damp and Mould",
    "Electrical Inspection",
    "Roofing",
    "Plumbing",
    "General Maintenance",
]
REPAIR_CATEGORIES = [
    "Boiler Repair",
    "Damp and Mould",
    "Electrical Inspection",
    "Fire Door Replacement",
    "Roof Leak",
    "Plumbing Repair",
    "Window Repair",
    "Heating Failure",
]
REPAIR_STATUSES = ["Reported", "Scheduled", "In Progress", "Completed"]
FOI_REQUEST_TYPES = [
    "Repairs History",
    "Electrical Safety",
    "Roof and Structural Repairs",
    "Fire Safety",
    "Tenancy and Repairs",
    "Contractor Attendance Records",
    "Inspection History",
]
FOI_STATUSES = ["Open", "In Review", "Responded", "Closed"]
CASEWORKERS = ["Caseworker A", "Caseworker B", "Caseworker C", "Caseworker D"]

REPAIR_TO_SPECIALISM_MAP = {
    "Boiler Repair": ["Boiler Repair"],
    "Damp and Mould": ["Damp and Mould"],
    "Electrical Inspection": ["Electrical Inspection"],
    "Fire Door Replacement": ["Plumbing", "General Maintenance"],
    "Roof Leak": ["Roofing"],
    "Plumbing Repair": ["Plumbing"],
    "Window Repair": ["General Maintenance", "Plumbing"],
    "Heating Failure": ["Boiler Repair", "General Maintenance"],
}


def random_date(start_date: date, end_date: date) -> date:
    delta = end_date - start_date
    return start_date + timedelta(days=random.randint(0, delta.days))


def escape_sql(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").replace("'", "''").strip()


def generate_properties(count: int) -> None:
    print("-- Properties")
    for i in range(1, count + 1):
        uprn = f"UPRNX{i:05d}"
        address_line_1 = escape_sql(fake.street_address())
        city = escape_sql(fake.city())
        postcode = escape_sql(fake.postcode())
        property_type = random.choice(PROPERTY_TYPES)
        bedrooms = random.randint(1, 5)
        build_year = random.randint(1960, 2023)
        compliance_status = random.choice(COMPLIANCE_STATUSES)
        inspection_date = random_date(date(2025, 1, 1), date(2026, 4, 1))

        print(
            "INSERT INTO properties "
            "(uprn, address_line_1, address_line_2, city, postcode, property_type, bedrooms, build_year, compliance_status, last_inspection_date) "
            f"VALUES ('{uprn}', '{address_line_1}', NULL, '{city}', '{postcode}', '{property_type}', {bedrooms}, {build_year}, '{compliance_status}', '{inspection_date}');"
        )


def generate_tenants(count: int, max_property_id: int) -> dict[int, int]:
    print("\n-- Tenants")
    tenant_property_map: dict[int, int] = {}

    for tenant_id in range(1, count + 1):
        property_id = random.randint(1, max_property_id)
        tenant_property_map[tenant_id] = property_id

        first_name = escape_sql(fake.first_name())
        last_name = escape_sql(fake.last_name())
        dob = fake.date_of_birth(minimum_age=18, maximum_age=85)
        email = escape_sql(fake.email())
        phone = escape_sql(fake.phone_number())
        tenancy_start_date = random_date(date(2018, 1, 1), date(2025, 12, 31))

        print(
            "INSERT INTO tenants "
            "(property_id, first_name, last_name, date_of_birth, email, phone, tenancy_start_date, tenancy_end_date, is_primary_tenant) "
            f"VALUES ({property_id}, '{first_name}', '{last_name}', '{dob}', '{email}', '{phone}', '{tenancy_start_date}', NULL, {random.choice(['TRUE', 'FALSE'])});"
        )

    return tenant_property_map


def generate_contractors(count: int) -> dict[str, list[int]]:
    print("\n-- Contractors")
    contractor_specialism_map: dict[str, list[int]] = {}
    contractor_id = 1

    for specialism in CONTRACTOR_SPECIALISMS:
        contractor_name = escape_sql(fake.company())
        email = escape_sql(fake.company_email())
        phone = escape_sql(fake.phone_number())

        contractor_specialism_map.setdefault(specialism, []).append(contractor_id)

        print(
            "INSERT INTO contractors "
            "(contractor_name, specialism, email, phone, active) "
            f"VALUES ('{contractor_name}', '{specialism}', '{email}', '{phone}', TRUE);"
        )

        contractor_id += 1

    remaining = count - len(CONTRACTOR_SPECIALISMS)
    for _ in range(remaining):
        specialism = random.choice(CONTRACTOR_SPECIALISMS)
        contractor_name = escape_sql(fake.company())
        email = escape_sql(fake.company_email())
        phone = escape_sql(fake.phone_number())

        contractor_specialism_map.setdefault(specialism, []).append(contractor_id)

        print(
            "INSERT INTO contractors "
            "(contractor_name, specialism, email, phone, active) "
            f"VALUES ('{contractor_name}', '{specialism}', '{email}', '{phone}', TRUE);"
        )

        contractor_id += 1

    return contractor_specialism_map


def generate_repair_records(
    count: int,
    max_property_id: int,
    contractor_specialism_map: dict[str, list[int]],
) -> None:
    print("\n-- Repair Records")

    for _ in range(count):
        property_id = random.randint(1, max_property_id)
        reported_date = random_date(date(2025, 1, 1), date(2026, 3, 1))
        scheduled_date = reported_date + timedelta(days=random.randint(1, 10))
        status = random.choice(REPAIR_STATUSES)

        completed_date = "NULL"
        if status == "Completed":
            completed_date_value = scheduled_date + timedelta(days=random.randint(0, 5))
            completed_date = f"'{completed_date_value}'"

        repair_category = random.choice(REPAIR_CATEGORIES)

        valid_specialisms = REPAIR_TO_SPECIALISM_MAP.get(repair_category, ["General Maintenance"])

        available_contractor_ids: list[int] = []
        for specialism in valid_specialisms:
            available_contractor_ids.extend(contractor_specialism_map.get(specialism, []))

        if available_contractor_ids:
            contractor_id = random.choice(available_contractor_ids)
        else:
            contractor_id = 1

        description = escape_sql(fake.sentence(nb_words=8))
        notes = escape_sql(fake.sentence(nb_words=12))
        cost = round(random.uniform(75, 1500), 2)

        print(
            "INSERT INTO repair_records "
            "(property_id, contractor_id, reported_date, scheduled_date, completed_date, repair_category, description, status, cost, notes) "
            f"VALUES ({property_id}, {contractor_id}, '{reported_date}', '{scheduled_date}', {completed_date}, '{repair_category}', '{description}', '{status}', {cost}, '{notes}');"
        )


def generate_foi_requests(count: int, tenant_property_map: dict[int, int]) -> None:
    print("\n-- FOI Requests")
    tenant_ids = list(tenant_property_map.keys())

    for i in range(1, count + 1):
        tenant_id = random.choice(tenant_ids)
        property_id = tenant_property_map[tenant_id]

        request_reference = f"FOI-2026-{1000 + i:04d}"
        request_date = random_date(date(2026, 1, 1), date(2026, 4, 1))
        due_date = request_date + timedelta(days=30)
        request_type = random.choice(FOI_REQUEST_TYPES)
        request_summary = escape_sql(fake.sentence(nb_words=14))
        status = random.choice(FOI_STATUSES)
        assigned_to = random.choice(CASEWORKERS)

        response_date = "NULL"
        if status in ["Responded", "Closed"]:
            response_date_value = request_date + timedelta(days=random.randint(5, 25))
            response_date = f"'{response_date_value}'"

        print(
            "INSERT INTO foi_requests "
            "(tenant_id, property_id, request_reference, request_date, due_date, request_type, request_summary, status, assigned_to, response_date) "
            f"VALUES ({tenant_id}, {property_id}, '{request_reference}', '{request_date}', '{due_date}', '{request_type}', '{request_summary}', '{status}', '{assigned_to}', {response_date});"
        )


def main() -> None:
    property_count = 25
    tenant_count = 40
    contractor_count = 10
    repair_count = 60
    foi_request_count = 25

    print("-- Synthetic seed data generated for the housing association compliance demo database")
    generate_properties(property_count)
    tenant_property_map = generate_tenants(tenant_count, property_count)
    contractor_specialism_map = generate_contractors(contractor_count)
    generate_repair_records(repair_count, property_count, contractor_specialism_map)
    generate_foi_requests(foi_request_count, tenant_property_map)


if __name__ == "__main__":
    main()