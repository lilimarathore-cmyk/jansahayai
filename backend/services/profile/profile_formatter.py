# backend/services/profile/profile_formatter.py
"""Format user profile for display"""

from typing import Dict


class ProfileFormatter:
    """Format profile for user display"""
    
    @staticmethod
    def format_summary(profile: Dict) -> str:
        """Format profile summary"""
        if not profile:
            return ""
        
        lines = ["📋 **Aapke dwara di gayi jankari:**"]
        
        if profile.get("age"):
            lines.append(f"   • Age: {profile['age']} saal")
        if profile.get("gender"):
            lines.append(f"   • Gender: {profile['gender']}")
        if profile.get("disability_type"):
            lines.append(f"   • Disability: {profile['disability_type']}")
        elif profile.get("disability_percentage"):
            lines.append(f"   • Disability: {profile['disability_percentage']}%")
        if profile.get("is_student"):
            student_line = "   • Student: Haan"
            if profile.get("class_grade"):
                student_line += f" (Class {profile['class_grade']})"
            lines.append(student_line)
        if profile.get("annual_income") or profile.get("income"):
            income = profile.get("annual_income") or profile.get("income")
            lines.append(f"   • Annual Income: ₹{income:,}")
        if profile.get("bpl_status") == "yes":
            lines.append("   • BPL: Haan ✅")
        
        return "\n".join(lines)


profile_formatter = ProfileFormatter()