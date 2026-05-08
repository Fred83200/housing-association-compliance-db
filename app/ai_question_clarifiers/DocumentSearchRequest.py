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

    def generate_where_clause(self) -> str:
        prompt = f"""
        You are generating a SQL WHERE clause for a PostgreSQL database to return information on these properties.

        The Relevant Schema:
        {self.get_schema_context()}

        Rules:
        - ONLY return the WHERE clause condition (NO 'WHERE' keyword)
        - Use valid PostgreSQL syntax
        - Use ILIKE for text matching
        - Use % for partial matches
        - Use correct column names EXACTLY as given
        - DO NOT include SELECT, DROP, INSERT, UPDATE, DELETE
        - DO NOT include comments (--)

        If no filtering is needed, return:
        TRUE

        Examples:

        Query: "non compliant properties in SW postcode"
        Output:
        postcode ILIKE 'SW%'

        Query: "properties in London inspected after 2023"
        Output:
        city ILIKE '%London%' AND last_inspection_date > '2023-01-01'

        """

        print(prompt)

        result = llm_generate_response([
            {"role": "user", "content": prompt}
        ])

        return result.strip()

    def generate_sql_query(self, where_clause) -> str:
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

        schema_info = self.get_schema_context()

        prompt = f"""
        Extract any possible identifiers mentioned in the following text for property information to use as a where clause to filter an SQL query. The schema of the properties table is provided.
        
        You are generating a SQL WHERE clause for a PostgreSQL database to return information on these properties.

        Rules:
        - ONLY return the WHERE clause condition (NO 'WHERE' keyword)
        - Use valid PostgreSQL syntax
        - Use ILIKE for text matching
        - Use % for partial matches
        - Use correct column names EXACTLY as given
        - DO NOT include SELECT, DROP, INSERT, UPDATE, DELETE
        - DO NOT include comments (--)
        
        Schema:
        {schema_info}

        Text:
        {combined}
        """

        result = llm_generate_response([
            {"role": "user", "content": prompt}
        ])

        try:
            return result.strip()
        except:
            return []

    def execute(self) -> dict:

        docs = self.semantic_document_search(self.question)

        property_ids_where_clause = (self.extract_property_ids_llm(docs))

        print(property_ids_where_clause)

        where_clause = str(property_ids_where_clause)

        query = self.generate_sql_query(where_clause)

        print(query)

        rows = self.run_query_and_get_rows(query)

        print(rows)

        answer = self.summarise_documents(self.question, docs, rows)

        return {
            "intent": self.intent,
            "answer": answer,
            "data": {
                "documents": docs,
                "properties": rows
            },
        }