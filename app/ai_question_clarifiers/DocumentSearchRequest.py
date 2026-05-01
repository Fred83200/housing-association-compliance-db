import json
import re

from app.ai_question_clarifiers.BaseQuestionClassifier import BaseQuestionClassifier
from app.llm_client import llm_generate_response
from app.vector_store import doc_store
from app.discovery_service import get_property_overview


class DocumentSearchRequest(BaseQuestionClassifier):

    def semantic_document_search(self, query: str):
        return doc_store.search(query)

    def summarise_documents(self, query: str, docs: list[dict], properties: list[dict]):

        if not docs and not properties:
            return f"No relevant information found for: '{query}'."

        doc_text = "\n\n".join([d["text"][:800] for d in docs])
        prop_text = properties[:5]  # limit

        prompt = f"""
        You are drafting a response to a UK housing association FOI request.

        User question:
        {query}

        Document evidence:
        {doc_text}

        Related property data:
        {prop_text}

        Instructions:
        - Combine BOTH document evidence and structured data
        - Clearly state which properties are affected
        - Highlight recurring issues if present
        - Keep it concise and professional
        - Do NOT mention systems or data sources
        - If only documents are available, rely on them
        - If only structured data is available, rely on that
        - If both are available, combine insights

        Response:
        """

        return llm_generate_response([
            {"role": "user", "content": prompt}
        ]).strip()



    def extract_property_ids(self, docs: list[dict]) -> list[int]:
        property_ids = set()

        for doc in docs:
            text = doc["text"]

            matches = re.findall(r"Property ID:\s*(\d+)", text)

            for m in matches:
                property_ids.add(int(m))

        return list(property_ids)

    def generate_sql_query(self, where_clause: str = "TRUE") -> str:
        return f"""
            SELECT
                property_id,
                uprn,
                address_line_1,
                city,
                postcode,
                compliance_status,
                last_inspection_date
            FROM properties
            WHERE {where_clause}
            ORDER BY last_inspection_date DESC
            LIMIT 20;
        """

    def extract_property_ids_llm(self, docs):

        combined = "\n\n".join([d["text"][:500] for d in docs])

        prompt = f"""
        Extract any property IDs mentioned in the following text.

        Return ONLY a JSON list of integers.

        Text:
        {combined}
        """

        result = llm_generate_response([
            {"role": "user", "content": prompt}
        ])

        try:
            return json.loads(result)
        except:
            return []

    def execute(self) -> dict:

        docs = self.semantic_document_search(self.question)

        raw_where = self.generate_where_clause()
        where_clause = self.sanitize_where_clause(raw_where)

        query = self.generate_sql_query(where_clause)
        rows = self.run_query_and_get_rows(query)

        property_ids = set(self.extract_property_ids(docs))
        property_ids.update(self.extract_property_ids_llm(docs))

        doc_linked_properties = []
        for pid in property_ids:
            prop = get_property_overview(pid)
            if prop:
                doc_linked_properties.append(prop)

        all_properties = {p["property_id"]: p for p in (rows + doc_linked_properties)}
        properties = list(all_properties.values())

        answer = self.summarise_documents(self.question, docs, properties)

        return {
            "intent": self.intent,
            "answer": answer,
            "data": {
                "documents": docs,
                "properties": properties
            },
        }