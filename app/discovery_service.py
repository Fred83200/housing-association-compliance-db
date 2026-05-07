from app.database import db_cursor

# SQL Injection checks

def sanitize_where_clause(where_clause: str) -> str:
    if not where_clause:
        return "TRUE"

    blocked = [";", "drop", "delete", "insert", "update", "--"]

    if any(word in where_clause.lower() for word in blocked):
        return "TRUE"

    if " or " in where_clause.lower():
        return "TRUE"

    return where_clause



def find_property(search_term: str) -> list[dict]:
    query = """
        SELECT
            property_id,
            uprn,
            address_line_1,
            city,
            postcode,
            property_type,
            compliance_status
        FROM properties
        WHERE
            LOWER(address_line_1) LIKE LOWER(%s)
            OR LOWER(postcode) LIKE LOWER(%s)
            OR LOWER(uprn) LIKE LOWER(%s)
        ORDER BY property_id
        LIMIT 10;
    """

    like_term = f"%{search_term}%"

    with db_cursor() as cursor:
        cursor.execute(query, (like_term, like_term, like_term))
        return cursor.fetchall()


def get_property_overview(property_id: int) -> dict | None:
    query = """
        SELECT *
        FROM vw_property_overview
        WHERE property_id = %s
        LIMIT 1;
    """

    with db_cursor() as cursor:
        cursor.execute(query, (property_id,))
        return cursor.fetchone()


def get_property_repairs(property_id: int) -> list[dict]:
    query = """
        SELECT
            repair_id,
            repair_category,
            description,
            status,
            reported_date,
            scheduled_date,
            completed_date,
            contractor_name,
            specialism
        FROM vw_property_repair_history
        WHERE property_id = %s
        ORDER BY reported_date DESC
        LIMIT 20;
    """

    with db_cursor() as cursor:
        cursor.execute(query, (property_id,))
        return cursor.fetchall()


def get_property_foi_requests(property_id: int) -> list[dict]:
    query = """
        SELECT
            request_reference,
            request_date,
            due_date,
            request_type,
            request_summary,
            status,
            assigned_to,
            response_date,
            first_name,
            last_name
        FROM vw_property_foi_requests
        WHERE property_id = %s
        ORDER BY request_date DESC
        LIMIT 20;
    """

    with db_cursor() as cursor:
        cursor.execute(query, (property_id,))
        return cursor.fetchall()


def get_non_compliant_properties(where_clause: str = "TRUE") -> list[dict]:
    query = f"""
        SELECT
            property_id,
            uprn,
            address_line_1,
            city,
            postcode,
            compliance_status,
            last_inspection_date
        FROM properties
        WHERE compliance_status = 'Non-Compliant'
        AND ({where_clause})
        ORDER BY last_inspection_date ASC
        LIMIT 20;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_all_foi_requests() -> list[dict]:
    query = """
        SELECT
            request_reference,
            request_date,
            due_date,
            request_type,
            request_summary,
            status,
            assigned_to,
            response_date,
            address_line_1,
            first_name,
            last_name
        FROM vw_property_foi_requests
        ORDER BY
            CASE WHEN response_date IS NULL THEN 0 ELSE 1 END,
            due_date ASC
        LIMIT 50;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_overdue_foi_requests() -> list[dict]:
    query = """
        SELECT
            request_reference,
            request_type,
            status,
            due_date,
            assigned_to,
            property_id,
            first_name,
            last_name,
            address_line_1,
            postcode
        FROM vw_property_foi_requests
        WHERE due_date < CURRENT_DATE
          AND response_date IS NULL
        ORDER BY due_date ASC
        LIMIT 20;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

def get_compliant_properties() -> list[dict]:
    query = """
        SELECT
            property_id,
            uprn,
            address_line_1,
            city,
            postcode,
            compliance_status,
            last_inspection_date
        FROM properties
        WHERE compliance_status = 'Compliant'
        ORDER BY last_inspection_date DESC
        LIMIT 20;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_properties_by_city(city: str) -> list[dict]:
    query = """
        SELECT
            property_id,
            uprn,
            address_line_1,
            city,
            postcode,
            property_type,
            compliance_status,
            last_inspection_date
        FROM properties
        WHERE LOWER(city) = LOWER(%s)
        ORDER BY property_id
        LIMIT 20;
    """

    with db_cursor() as cursor:
        cursor.execute(query, (city,))
        return cursor.fetchall()


def get_overdue_inspections() -> list[dict]:
    query = """
        SELECT
            property_id,
            uprn,
            address_line_1,
            city,
            postcode,
            compliance_status,
            last_inspection_date
        FROM properties
        WHERE last_inspection_date < CURRENT_DATE - INTERVAL '365 days'
        ORDER BY last_inspection_date ASC
        LIMIT 20;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_properties_inspected_after(inspection_date: str) -> list[dict]:
    query = """
        SELECT
            property_id,
            uprn,
            address_line_1,
            city,
            postcode,
            compliance_status,
            last_inspection_date
        FROM properties
        WHERE last_inspection_date > %s
        ORDER BY last_inspection_date ASC
        LIMIT 20;
    """

    with db_cursor() as cursor:
        cursor.execute(query, (inspection_date,))
        return cursor.fetchall()