from app.ai_question_clarifiers.BaseQuestionClassifier import BaseQuestionClassifier

class PropertyCaseFileRequest(BaseQuestionClassifier):
    def generate_sql_query(self, where_clause: str = "TRUE") -> str:
        pass

    def get_schema_context(self) -> str:
        return """
        Tables:

        properties:
        - property_id
        - address_line_1
        - city
        - postcode
        - compliance_status

        tenants:
        - tenant_id
        - property_id
        - first_name
        - last_name

        repair_records:
        - property_id
        - repair_category
        - status
        - reported_date

        foi_requests:
        - property_id
        - request_reference
        - status
        - due_date

        Relationships:
        - tenants.property_id → properties.property_id
        - repair_records.property_id → properties.property_id
        - foi_requests.property_id → properties.property_id

        Note:
        - property_id is the main lookup key
        """
