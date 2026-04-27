from app.database import db_cursor


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

    def generate_response(self) -> dict:

        rows = self.run_query_and_get_rows(self.generate_sql_query(self.where_clause))

        return {
            "intent": self.intent,
            "answer": self.create_success_message() if rows else self.create_failure_message(),
            "data": rows,
        }

    def generate_sql_query(self, where_clause: str = "TRUE") -> str:
        raise NotImplementedError("Subclasses must implement generate_sql_query")

    def run_query_and_get_rows(self, query: str = '') -> list[dict]:
        if not query:
            query = self.generate_sql_query(self.where_clause)
        with db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
