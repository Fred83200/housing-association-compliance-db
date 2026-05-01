from app.ai_question_clarifiers.BaseQuestionClassifier import BaseQuestionClassifier

class FindPropertyRequest(BaseQuestionClassifier):

    def generate_sql_query(self, where_clause: str = "TRUE") -> str:
        query = f"""
                SELECT
                    property_id,
                    uprn,
                    address_line_1,
                    city,
                    postcode,
                    property_type,
                    compliance_status
                FROM properties
                WHERE {where_clause}
                ORDER BY property_id
                LIMIT 10;
            """
        return query

    def get_schema_context(self) -> str:
        return """
        Tables:

        foi_requests:
        - foi_request_id (integer)
        - tenant_id (integer)
        - property_id (integer)
        - request_reference (text)
        - request_date (date)
        - due_date (date)
        - request_type (text)
        - request_summary (text)
        - status (text)
        - assigned_to (text)
        - response_date (date)

        properties:
        - property_id (integer)
        - postcode (text)
        - city (text)

        Relationships:
        - foi_requests.property_id → properties.property_id

        Filtering rules:
        - overdue → due_date < CURRENT_DATE AND response_date IS NULL
        - postcode → properties.postcode ILIKE 'SW1%'
        - city → properties.city ILIKE 'London'
        """
