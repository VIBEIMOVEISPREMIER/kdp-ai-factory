class LicenseService:
    def register_trial(self, machine_id):
        return {"registered": True, "machine_id": machine_id, "books_created": 0, "free_books_remaining": 1}

    def activate(self, machine_id, token):
        return {"valid": False, "reason": "not configured"}

    def verify_payment(self, tx_id, asset):
        return {"verified": False, "reason": "not configured"}
