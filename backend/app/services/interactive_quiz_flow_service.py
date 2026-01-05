from typing import Dict, List


class InteractiveQuizFlowService:
    """
    Hikâye içine gömülü mini-quiz akışları için basit kurgusal servis.
    """

    async def generate_inline_quiz(self, story_text: str, count: int = 3) -> Dict:
        questions: List[Dict] = []
        for i in range(count):
            questions.append(
                {
                    "id": f"q{i+1}",
                    "question": f"Hikâyedeki ana duygu nedir? ({i+1})",
                    "options": ["Neşe", "Korku", "Merak"],
                    "correct": "Merak",
                    "insert_after_char": min(len(story_text), (i + 1) * 50),
                }
            )
        return {"questions": questions}

    async def evaluate(self, answers: Dict[str, str]) -> Dict:
        score = sum(1 for v in answers.values() if v == "Merak")
        return {"score": score, "total": len(answers)}


