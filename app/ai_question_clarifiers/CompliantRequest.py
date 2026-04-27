from app.ai_question_clarifiers.BaseQuestionClassifier import BaseQuestionClassifier

class CompliantRequest(BaseQuestionClassifier):

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
                WHERE compliance_status = 'Compliant'
                AND ({where_clause})
                ORDER BY last_inspection_date DESC
                LIMIT 20;
            """
        return query
