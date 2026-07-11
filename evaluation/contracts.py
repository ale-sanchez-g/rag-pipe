from pydantic import BaseModel


class RagasScores(BaseModel):
    faithfulness: float
    context_precision: float
    context_recall: float
    answer_relevancy: float
