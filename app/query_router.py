import json

from app.llm_client import llm_generate_response
from app.configs import Configs
from app.discovery_service import (
    find_property,
    get_boiler_repair_records,
    get_compliant_properties,
    get_non_compliant_properties,
    get_open_foi_requests,
    get_overdue_foi_requests,
    get_overdue_inspections,
    get_properties_by_city,
    get_properties_inspected_after,
    get_properties_with_damp_issues,
    get_property_foi_requests,
    get_property_overview,
    get_property_repairs,
)
from app.document_retrieval_service import (
    search_documents,
    search_documents_for_property,
)

configs = Configs()


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


def classify_intent(user_query: str) -> str:
    prompt = f"""
                Classify the user query into ONE of these intents (The default should be document_search):
                
                Only classify as one of the other intents if they specifically mention the intent.
                
                - document_search (if the user mentions documents, reports, emails, notes, or evidence)
                - non_compliant_properties (If they specifically ask for non compliant properties)
                - compliant_properties (If they specifically ask for compliant properties)
                - overdue_inspections (If they specifically ask for overdue inspections)
                - overdue_foi_requests (If they specifically ask for overdue foi requests)
                - property_case_file (If they specifically ask for property case files)
                
                                    
                Return ONLY JSON:
                {{
                  "intent": "..."
                }}
                
                User Query: {user_query}
                """

    result = llm_generate_response([
        {"role": "user", "content": prompt}
    ])

    try:
        return json.loads(result).get("intent", "unknown")
    except:
        return "unknown"


def answer_question(question: str) -> dict:
    normalized_question = question.lower().strip()

    if not normalized_question:
        return {
            "intent": "empty_question",
            "answer": "Please enter a question.",
            "data": [],
        }

    if "boiler" in normalized_question and "repair" in normalized_question:
        rows = get_boiler_repair_records()
        return _build_response(
            "boiler_repair_records",
            "I found the following boiler repair records.",
            "I could not find any boiler repair records.",
            rows,
        )

    if (
        ("open" in normalized_question or "active" in normalized_question or "list" in normalized_question)
        and ("foi" in normalized_question or "stairs" in normalized_question or "request" in normalized_question)
    ):
        rows = get_open_foi_requests()
        return _build_response(
            "open_foi_requests",
            "I found the following open STAIRS / FOI requests.",
            "I could not find any open STAIRS / FOI requests.",
            rows,
        )

    if (
        "damp" in normalized_question
        or "mould" in normalized_question
        or "mold" in normalized_question
    ):
        rows = get_properties_with_damp_issues()
        return _build_response(
            "properties_with_damp_issues",
            "I found the following properties with damp or mould issues.",
            "I could not find any properties with damp or mould issues.",
            rows,
        )

    # AI routing stuff first, fallback to keyword matching if nothing works

    ai_intent = classify_intent(normalized_question)
    intent = ai_intent

    print("PARSED INTENT:", ai_intent)

    # Fallback to keyword counting if AI search doesn't retrieve anything

    try:
        request_type_class_selection = configs.clarifier_class_dict[intent]
        request_type_class = request_type_class_selection(intent, question)
        response = request_type_class.execute()

        if "could" in response.get("answer"):
            pass
        else:
            return response
    except KeyError:
        pass

    # Keyword matching

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