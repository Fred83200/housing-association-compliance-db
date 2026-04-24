from app.discovery_service import (
    find_property,
    get_compliant_properties,
    get_non_compliant_properties,
    get_overdue_foi_requests,
    get_overdue_inspections,
    get_properties_by_city,
    get_properties_inspected_after,
    get_property_foi_requests,
    get_property_overview,
    get_property_repairs,
)


def answer_question(question: str) -> dict:
    normalized_question = question.lower().strip()

    def build_response(intent: str, success_msg: str, empty_msg: str, rows: list) -> dict:
        return {
            "intent": intent,
            "answer": success_msg if rows else empty_msg,
            "data": rows,
        }

    if "non-compliant" in normalized_question or "non compliant" in normalized_question:
        rows = get_non_compliant_properties()
        return build_response(
            "non_compliant_properties",
            "I found the following non-compliant properties.",
            "I could not find any non-compliant properties.",
            rows,
        )

    if "compliant" in normalized_question:
        rows = get_compliant_properties()
        return build_response(
            "compliant_properties",
            "I found the following compliant properties.",
            "I could not find any compliant properties.",
            rows,
        )

    if "overdue" in normalized_question and "inspection" in normalized_question:
        rows = get_overdue_inspections()
        return build_response(
            "overdue_inspections",
            "I found the following overdue inspections.",
            "I could not find any overdue inspections.",
            rows,
        )

    if "inspected after" in normalized_question:
        inspection_date = normalized_question.split("after")[-1].strip()
        rows = get_properties_inspected_after(inspection_date)
        return build_response(
            "inspected_after_date",
            f"I found properties inspected after {inspection_date}.",
            f"I could not find any properties inspected after {inspection_date}.",
            rows,
        )

    if "properties in" in normalized_question:
        city = (
            normalized_question
            .replace("show me", "")
            .replace("properties in", "")
            .strip()
        )
        rows = get_properties_by_city(city)
        return build_response(
            "properties_by_city",
            f"I found properties in {city}.",
            f"I could not find any properties in {city}.",
            rows,
        )

    if "overdue" in normalized_question and (
        "foi" in normalized_question or "request" in normalized_question
    ):
        rows = get_overdue_foi_requests()
        return build_response(
            "overdue_foi_requests",
            "I found the following overdue FOI requests.",
            "I could not find any overdue FOI requests.",
            rows,
        )

    if (
        "property" in normalized_question
        or "postcode" in normalized_question
        or "uprn" in normalized_question
    ):
        search_term = (
            normalized_question.replace("property", "")
            .replace("postcode", "")
            .replace("uprn", "")
            .replace("show me", "")
            .replace("find", "")
            .strip()
        )

        properties = find_property(search_term)

        return build_response(
            "find_property",
            "I found the following matching properties.",
            "I could not find any matching properties.",
            properties,
        )

    return {
        "intent": "unknown",
        "answer": (
            "I could not confidently identify the request. "
            "Try asking about a property, postcode, compliant properties, "
            "non-compliant properties, overdue inspections, or overdue FOI requests."
        ),
        "data": [],
    }


def build_property_case_file(property_id: int) -> dict:
    overview = get_property_overview(property_id)
    repairs = get_property_repairs(property_id)
    foi_requests = get_property_foi_requests(property_id)

    return {
        "property_id": property_id,
        "overview": overview,
        "repairs": repairs,
        "foi_requests": foi_requests,
    }