from datetime import datetime
from backend.config import (
    SCORING_WEIGHTS, 
    PRIORITY_THRESHOLDS, 
    URGENT_KEYWORDS, 
    VIP_SENDERS
)

class PriorityEngine:
    """
    Core logic for determining notification importance.
    Uses a weighted scoring system based on keywords, sender reputation, and source metadata.
    """

    def process(self, notifications):
        """
        Ingests raw notifications and appends 'priority_score' (0-100) and 'priority' labels.
        """
        processed = []
        for note in notifications:
            # 1. Check for pre-assigned priority (e.g. from upstream integrations)
            # If a source explicitly marks an item as urgent, we respect that override.
            current_priority = note.get("priority", "normal")
            
            if current_priority == "urgent":
                note["priority_score"] = 95
                note["priority_reasons"] = ["Critical Source Alert"]
                processed.append(note)
                continue

            if current_priority == "high":
                note["priority_score"] = 80
                note["priority_reasons"] = ["High Importance Source"]
                processed.append(note)
                continue

            # 2. Calculate dynamic score for unlabelled items
            score, reasons = self._calculate_score(note)
            
            # 3. Assign label and finalize
            note["priority_score"] = score
            note["priority"] = self._assign_label(score)
            note["priority_reasons"] = reasons
            
            processed.append(note)
            
        # Sort by Priority Score descending (Urgent first)
        return sorted(processed, key=lambda x: x["priority_score"], reverse=True)

    def _calculate_score(self, note):
        score = 10 # Base score
        reasons = []

        # A. Keyword Analysis
        # Checks against both config-defined keywords and an internal critical set
        local_urgent_words = ['urgent', 'down', 'crash', 'error', 'fail', 'alert', 'critical', 'sev-1']
        
        full_text = (note.get("title", "") + " " + note.get("content", "")).lower()
        
        for word in URGENT_KEYWORDS:
            if word in full_text:
                score += SCORING_WEIGHTS.get("keyword_match", 20)
                reasons.append(f"Keyword Match: '{word}'")
                break
        
        if any(w in full_text for w in local_urgent_words):
             score += 30
             reasons.append("Critical Terminology")

        # B. Sender Reputation
        sender_email = note.get("sender", {}).get("email", "").lower()
        sender_name = note.get("sender", {}).get("name", "").lower()
        
        if any(vip in sender_email or vip in sender_name for vip in VIP_SENDERS):
            score += SCORING_WEIGHTS.get("vip_sender", 30)
            reasons.append("VIP Sender")

        # C. Contextual Metadata (DMs, Mentions)
        notif_type = note.get("type", "").lower()
        tags = note.get("tags", [])
        
        if notif_type == "dm" or "dm" in tags:
            score += SCORING_WEIGHTS.get("is_direct_message", 20)
            reasons.append("Direct Message")
            
        if notif_type == "mention" or "mention" in tags:
            score += SCORING_WEIGHTS.get("is_mention", 20)
            reasons.append("Direct Mention")

        return min(score, 100), reasons

    def _assign_label(self, score):
        if score >= PRIORITY_THRESHOLDS.get("urgent", 85):
            return "urgent"
        elif score >= PRIORITY_THRESHOLDS.get("high", 50):
            return "high"
        elif score >= PRIORITY_THRESHOLDS.get("normal", 20):
            return "normal"
        return "low"