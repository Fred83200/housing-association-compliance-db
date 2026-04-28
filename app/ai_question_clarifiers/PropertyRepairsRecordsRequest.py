from app.ai_question_clarifiers.BaseQuestionClassifier import BaseQuestionClassifier

class PropertyRepairsRecordsRequest(BaseQuestionClassifier):
    def generate_sql_query(self, where_clause: str = "TRUE") -> str:
        query = f"""
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
                WHERE {where_clause}
                ORDER BY reported_date DESC
                LIMIT 20;
            """
        return query

    def get_schema_context(self) -> str:
        return """
        Tables:

        repair_records:
        - repair_id (integer)
        - property_id (integer)
        - contractor_id (integer)
        - reported_date (date)
        - scheduled_date (date)
        - completed_date (date)
        - repair_category (text)
        - description (text)
        - status (text)
        - cost (numeric)

        properties:
        - property_id (integer)
        - postcode (text)
        - city (text)

        Relationships:
        - repair_records.property_id → properties.property_id

        Filtering rules:
        - dates → compare using > or <
        - postcode → properties.postcode ILIKE 'SW1%'
        """
