from app.ai_question_clarifiers.BaseQuestionClassifier import BaseQuestionClassifier

class OverdueFOIRequest(BaseQuestionClassifier):

    def generate_sql_query(self, where_clause: str = "TRUE") -> str:
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
                WHERE last_inspection_date < CURRENT_DATE - INTERVAL '30 days'
                AND ({where_clause})
                ORDER BY last_inspection_date ASC
                LIMIT 20;
            """
        return query
