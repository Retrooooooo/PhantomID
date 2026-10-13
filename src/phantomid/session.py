class AnomalyCounter:
    """Count fresh evaluations, never repeatedly count the same evidence."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.consecutive = 0
        self.last_evidence = -1
        self.challenged = False

    def evaluate(self, evidence_id, abnormal):
        if self.challenged or evidence_id <= self.last_evidence:
            return False
        self.last_evidence = evidence_id
        self.consecutive = self.consecutive + 1 if abnormal is True else 0
        self.challenged = self.consecutive >= 3
        return self.challenged
