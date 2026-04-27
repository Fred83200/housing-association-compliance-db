from app.ai_question_clarifiers.NonCompliantRequest import NonCompliantRequest
from app.ai_question_clarifiers.CompliantRequest import CompliantRequest
from app.ai_question_clarifiers.OverdueFOIRequest import OverdueFOIRequest
from app.ai_question_clarifiers.OverdueInspectionsRequest import OverdueInspectionsRequest

class Configs:

    def __init__(self):
        self.clarifier_class_dict = {
            "compliant_properties": CompliantRequest,
            "non_compliant_properties": NonCompliantRequest,
            "overdue_inspections": OverdueInspectionsRequest,
            "overdue_foi_requests": OverdueFOIRequest,
        }
