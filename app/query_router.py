import json

from app.llm_client import generate_response
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
from app.document_retrieval_service import (
    search_documents,
    search_documents_for_property,
)


def _build_response(intent: str, success_msg: str, empty_msg: str, rows: list) -> dict:
    return {
        "intent": intent,
        "answer": success_msg if rows else empty_msg,
        "data": rows,
    }


def _extract_property_id(normalized_question: str) -> int | None:
    """
    Extracts property ID from simple phrases like:
    - show me everything for property 1
    - case file for property 1
    - show me case file property 1
    """

    words = normalized_question.replace("#", " ").split()

    for index, word in enumerate(words):
        if word == "property" and index + 1 < len(words):
            possible_id = words[index + 1].strip()

            if possible_id.isdigit():
                return int(possible_id)

    last_word = words[-1] if words else ""

    if last_word.isdigit():
        return int(last_word)

    return None


def classify_query_ai(user_query: str) -> dict:
    prompt = prompt = f"""
You are an AI assistant for housing association FOI queries.

Your job is to classify the user's request into ONE of the following intents:

- non_compliant (properties not meeting compliance standards, unsafe, poor condition, failed inspections, bad condition)
- compliant (properties meeting standards)
- overdue_inspections (late or overdue inspections)
- inspected_after (properties inspected after a certain date)
- properties_by_city (properties in a specific location)
- overdue_foi (late FOI requests)
- property_case_file (full details for a specific property)
- document_search (reports, documents, notes)
- find_property (lookup by postcode, UPRN, or identifier)
- unknown

IMPORTANT:
- Map natural language to the closest intent
- "bad condition", "unsafe", "failing", "not up to standard" → non_compliant
- "late", "behind", "overdue" → overdue_inspections or overdue_foi
- Be flexible in interpretation

Return ONLY valid JSON:

{{
  "intent": "...",
  "property_id": number or null,
  "city": string or null,
  "date": string or null,
  "keywords": []
}}

Query: {user_query}
"""

    result = generate_response([
        {"role": "user", "content": prompt}
    ])

    print("AI INTENT RAW:", result)

    try:
        return json.loads(result)
    except:
        return {"intent": "unknown"}


def answer_question(question: str) -> dict:
    normalized_question = question.lower().strip()

    ai_intent = classify_query_ai(question)
    intent = ai_intent.get("intent")
    
    print("PARSED INTENT:", ai_intent)

    if not normalized_question:
        return {
            "intent": "empty_question",
            "answer": "Please enter a question.",
            "data": [],
        }

    # ai routing stuff first, fallback to keyword matching if nothing works

    if intent == "non_compliant":
        rows = get_non_compliant_properties()
        return _build_response(
            "non_compliant_properties",
            "I found the following non-compliant properties (AI retrieved).",
            "I could not find any non-compliant properties.",
            rows,
        )

    if intent == "compliant":
        rows = get_compliant_properties()
        return _build_response(
            "compliant_properties",
            "I found the following compliant properties (AI retrieved).",
            "I could not find any compliant properties.",
            rows,
        )

    if intent == "overdue_inspections":
        rows = get_overdue_inspections()
        return _build_response(
            "overdue_inspections",
            "I found the following overdue inspections (AI retrieved).",
            "I could not find any overdue inspections.",
            rows,
        )

    if intent == "overdue_foi":
        rows = get_overdue_foi_requests()
        return _build_response(
            "overdue_foi_requests",
            "I found the following overdue FOI requests (AI retrieved).",
            "I could not find any overdue FOI requests.",
            rows,
        )

    if "non-compliant" in normalized_question or "non compliant" in normalized_question:
        rows = get_non_compliant_properties()
        return _build_response(
            "non_compliant_properties",
            "I found the following non-compliant properties.",
            "I could not find any non-compliant properties.",
            rows,
        )

    if "compliant" in normalized_question:
        rows = get_compliant_properties()
        return _build_response(
            "compliant_properties",
            "I found the following compliant properties.",
            "I could not find any compliant properties.",
            rows,
        )

    if "overdue" in normalized_question and "inspection" in normalized_question:
        rows = get_overdue_inspections()
        return _build_response(
            "overdue_inspections",
            "I found the following overdue inspections.",
            "I could not find any overdue inspections.",
            rows,
        )

    if "inspected after" in normalized_question:
        inspection_date = normalized_question.split("after")[-1].strip()
        rows = get_properties_inspected_after(inspection_date)
        return _build_response(
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
        return _build_response(
            "properties_by_city",
            f"I found properties in {city}.",
            f"I could not find any properties in {city}.",
            rows,
        )

    if "overdue" in normalized_question and (
        "foi" in normalized_question or "request" in normalized_question
    ):
        rows = get_overdue_foi_requests()
        return _build_response(
            "overdue_foi_requests",
            "I found the following overdue FOI requests.",
            "I could not find any overdue FOI requests.",
            rows,
        )

    if (
        "everything for property" in normalized_question
        or "case file for property" in normalized_question
        or "case-file for property" in normalized_question
        or "case file property" in normalized_question
        or "show me case file" in normalized_question
    ):
        property_id = _extract_property_id(normalized_question)

        if property_id is None:
            return {
                "intent": "property_case_file",
                "answer": "I could not identify the property ID. Try asking: Show me everything for property 1.",
                "data": {},
            }

        case_file = build_property_case_file(property_id)

        if case_file["overview"] is None:
            return {
                "intent": "property_case_file",
                "answer": f"I could not find property {property_id}.",
                "data": case_file,
            }

        return {
            "intent": "property_case_file",
            "answer": f"I found the structured records and document evidence for property {property_id}.",
            "data": case_file,
        }

    if (
        "document" in normalized_question
        or "documents" in normalized_question
        or "report" in normalized_question
        or "reports" in normalized_question
        or "notes" in normalized_question
    ):
        rows = search_documents([normalized_question])
        return _build_response(
            "document_search",
            "I found the following matching documents.",
            "I could not find any matching documents.",
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

        return _build_response(
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
            "non-compliant properties, overdue inspections, overdue FOI requests, "
            "or document reports."
        ),
        "data": [],
    }


def build_property_case_file(property_id: int) -> dict:
    overview = get_property_overview(property_id)
    repairs = get_property_repairs(property_id)
    foi_requests = get_property_foi_requests(property_id)

    if overview:
        documents = search_documents_for_property(
            property_id=property_id,
            uprn=overview.get("uprn"),
            postcode=overview.get("postcode"),
            extra_terms=[
                overview.get("address_line_1", ""),
                overview.get("compliance_status", ""),
            ],
        )
    else:
        documents = []

    return {
        "property_id": property_id,
        "overview": overview,
        "repairs": repairs,
        "foi_requests": foi_requests,
        "documents": documents,
    }