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

def get_dashboard_summary() -> dict:
    query = """
        SELECT
            COUNT(*) FILTER (WHERE compliance_status = 'Non-Compliant') AS non_compliant_properties,
            COUNT(*) FILTER (
                WHERE last_inspection_date < CURRENT_DATE - INTERVAL '365 days'
            ) AS overdue_inspections,
            COUNT(*) AS total_properties,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE compliance_status = 'Compliant') / NULLIF(COUNT(*), 0),
                0
            ) AS portfolio_compliance_rate
        FROM properties;
    """

    foi_query = """
        SELECT
            COUNT(*) FILTER (WHERE response_date IS NULL) AS active_stairs_requests,
            COUNT(*) FILTER (
                WHERE response_date IS NULL
                  AND due_date <= CURRENT_DATE + INTERVAL '7 days'
            ) AS stairs_due_within_7_days,
            COUNT(*) FILTER (
                WHERE response_date >= CURRENT_DATE - INTERVAL '30 days'
            ) AS released_last_30_days
        FROM foi_requests;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        property_summary = cursor.fetchone()

        cursor.execute(foi_query)
        foi_summary = cursor.fetchone()

        return {
            **property_summary,
            **foi_summary,
        }


def get_properties_requiring_attention() -> list[dict]:
    query = """
        SELECT
            property_id,
            uprn,
            address_line_1,
            city,
            postcode,
            compliance_status,
            last_inspection_date,
            CURRENT_DATE - last_inspection_date AS days_since_inspection
        FROM properties
        WHERE compliance_status = 'Non-Compliant'
           OR last_inspection_date < CURRENT_DATE - INTERVAL '365 days'
        ORDER BY
            CASE WHEN compliance_status = 'Non-Compliant' THEN 0 ELSE 1 END,
            last_inspection_date ASC
        LIMIT 50;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

def get_open_foi_requests() -> list[dict]:
    query = """
        SELECT
            request_reference,
            request_type,
            status,
            request_date,
            due_date,
            assigned_to,
            property_id,
            first_name,
            last_name,
            address_line_1,
            postcode
        FROM vw_property_foi_requests
        WHERE response_date IS NULL
        ORDER BY due_date ASC
        LIMIT 50;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_boiler_repair_records() -> list[dict]:
    query = """
        SELECT
            repair_id,
            property_id,
            uprn,
            address_line_1,
            postcode,
            repair_category,
            status,
            reported_date,
            completed_date,
            contractor_name
        FROM vw_property_repair_history
        WHERE LOWER(repair_category) LIKE '%boiler%'
           OR LOWER(description) LIKE '%boiler%'
           OR LOWER(description) LIKE '%heating%'
        ORDER BY reported_date DESC
        LIMIT 50;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_properties_with_damp_issues() -> list[dict]:
    query = """
        SELECT DISTINCT
            p.property_id,
            p.uprn,
            p.address_line_1,
            p.city,
            p.postcode,
            p.compliance_status,
            p.last_inspection_date
        FROM properties p
        LEFT JOIN repair_records r
            ON p.property_id = r.property_id
        WHERE LOWER(r.repair_category) LIKE '%damp%'
           OR LOWER(r.description) LIKE '%damp%'
           OR LOWER(r.description) LIKE '%mould%'
           OR LOWER(r.description) LIKE '%mold%'
        ORDER BY p.last_inspection_date ASC
        LIMIT 50;
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()