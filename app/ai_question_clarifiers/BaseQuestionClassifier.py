import json

from app.database import db_cursor
from app.llm_client import llm_generate_response


class BaseQuestionClassifier:

    def __init__(self, intent: str, question: str, where_clause: str = 'TRUE'):

        self.intent = intent
        self.question = question
        self.where_clause = where_clause

    def clean_intent_message(self, intent: str = ''):
        if not intent:
            intent = self.intent
            intent = intent.replace('_', ' ')
            intent = intent.capitalize()
        return intent

    def create_success_message(self, question: str = ''):
        intent = self.clean_intent_message()
        if not question:
            question = self.question
        success_msg = f"I found the following {intent} properties for your question: {question} (AI retrieved)."
        return success_msg

    def create_failure_message(self, question: str = ''):
        intent = self.clean_intent_message()
        if not question:
            question = self.question
        failure_message = f"I could not find any {intent} properties for your question: {question} (AI retrieved)."
        return failure_message

    def execute(self) -> dict:

        raw_where = self.generate_where_clause()

        where_clause = self.sanitize_where_clause(raw_where)

        query = self.generate_sql_query(where_clause)

        rows = self.run_query_and_get_rows(query)

        # print("---- DEBUG ----")
        # print("QUESTION:", self.question)
        # print("RAW WHERE:", raw_where)
        # print("SAFE WHERE:", where_clause)
        # print("SQL:", query)
        # print("----------------")

        return {
            "intent": self.intent,
            "answer": self.create_success_message() if rows else self.create_failure_message(),
            "data": rows,
        }

    def get_schema_context(self) -> str:
        return """
        Table: properties

        Columns:
        - property_id (integer: Identifier for the tables within our DB e.g '1')
        - uprn (text: UK standard ID value for the property e.g 'UPRNX00022')
        - address_line_1 (text: Full address of the property)
        - address_line_2 (text)
        - city (text: City of the property)
        - postcode (text: UK format e.g. "SW1A 1AA")
        - property_type (text: e.g 'House', 'Flat', 'Bungalow', 'Maisonette')
        - bedrooms (integer: How many bedrooms the property has)
        - build_year (integer: What year the property was built)
        - compliance_status (text: 'Compliant' or 'Non-Compliant', or 'Inspection Due')
        - last_inspection_date (date)

        Filtering rules:
        - postcode → use prefix match (postcode ILIKE 'SW1%')
        - city → use ILIKE (city ILIKE 'London')
        - last_inspection_date → supports > or < comparisons
        """

    def generate_where_clause(self) -> str:
        prompt = f"""
        You are generating a SQL WHERE clause for a PostgreSQL database for this user question: {self.question}.

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

        IMPORTANT:
        - compliance_status is already handled in the base query
        - DO NOT include compliance_status in the WHERE clause

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

    def sanitize_where_clause(self, where_clause: str) -> str:
        if not where_clause:
            return "TRUE"

        lowered = where_clause.lower()

        blocked = [
            "drop", "delete", "insert", "update",
            ";", "--"
        ]

        if any(b in lowered for b in blocked):
            return "TRUE"

        if " or " in lowered:
            return "TRUE"

        return where_clause

    def generate_sql_query(self, where_clause: str = "TRUE") -> str:
        raise NotImplementedError("Subclasses must implement generate_sql_query")

    def run_query_and_get_rows(self, query: str = '') -> list[dict]:
        if not query:
            query = self.generate_sql_query(self.where_clause)
        with db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
