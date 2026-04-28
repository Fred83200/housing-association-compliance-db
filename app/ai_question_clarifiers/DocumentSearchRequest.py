from app.ai_question_clarifiers.BaseQuestionClassifier import BaseQuestionClassifier
from app.llm_client import llm_generate_response
from app.vector_store import doc_store


class DocumentSearchRequest(BaseQuestionClassifier):

    def semantic_document_search(self, query: str):
        return doc_store.search(query)

    def summarise_documents(self, query: str, docs: list[dict]):

        if not docs:
            return f"No relevant documents were found for your request: '{query}'."

        # limit size
        combined_text = "\n\n".join([d["text"][:1000] for d in docs])

        prompt = f"""
        You are drafting a response to a housing association FOI-style query.

        User question:
        {query}

        Relevant document excerpts:
        {combined_text}

        Instructions:
        - Summarise key findings
        - Highlight important issues (e.g. safety, maintenance, repeated faults)
        - Keep it concise and professional
        - Do NOT mention files, embeddings, or technical systems

        Response:
        """

        return llm_generate_response([
            {"role": "user", "content": prompt}
        ]).strip()

    def execute(self) -> dict:

        docs = self.semantic_document_search(self.question)

        answer = self.summarise_documents(self.question, docs)

        return {
            "intent": self.intent,
            "answer": answer,
            "data": docs,
        }