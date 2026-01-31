"""Wellness domain model.

Standards: python_clean.mdc
- Enum for insight types
- Dataclass for domain models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class WellnessInsightType(str, Enum):
    """Type of wellness insight."""

    ENCOURAGEMENT = "encouragement"
    MILESTONE = "milestone"
    TIP = "tip"
    BURNOUT_WARNING = "burnout_warning"
    BREAK_REMINDER = "break_reminder"
    SUCCESS_STORY = "success_story"


@dataclass
class WellnessInsight:
    """A wellness insight/tip for the user."""

    insight_type: WellnessInsightType
    title: str
    message: str
    action_suggestion: str | None = None
    priority: int = 1  # 1=low, 2=medium, 3=high


@dataclass
class WellnessStatus:
    """User's overall wellness status."""

    user_id: str
    activity_level: str  # "low", "moderate", "high", "very_high"
    rejection_streak: int
    days_since_last_positive: int | None
    burnout_risk: str  # "low", "medium", "high"
    recommended_action: str
    last_checked: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BurnoutSignals:
    """Detected burnout signals."""

    consecutive_rejections: int
    hours_active_today: float
    declining_match_scores: bool
    panic_applying: bool  # Sudden increase in application rate
    no_breaks_taken: bool


# Predefined encouragement messages
ENCOURAGEMENT_MESSAGES = {
    "first_interview": [
        "Your first interview! All your effort is paying off.",
        "Congratulations on landing an interview! You've got this.",
        "Interview secured! Remember, they already like what they see.",
    ],
    "application_milestone_10": [
        "10 applications down! Consistency is key.",
        "You've applied to 10 jobs - that's dedication!",
        "10 applications sent! Each one is a step closer.",
    ],
    "application_milestone_25": [
        "25 applications! You're building serious momentum.",
        "A quarter century of applications! Keep the faith.",
        "25 and counting - your persistence will pay off.",
    ],
    "application_milestone_50": [
        "50 applications! You're a job search warrior.",
        "Half a hundred applications - your next role is coming.",
        "50 applications submitted! That's impressive dedication.",
    ],
    "streak_maintained": [
        "Another day, another step forward. Keep it up!",
        "Your streak continues! Small daily actions lead to big results.",
        "Consistency breeds success. Great job maintaining your streak!",
    ],
    "high_match_found": [
        "Found a job with a great match! This could be the one.",
        "High match score detected! This role seems perfect for you.",
        "Looks like we found a strong match! Give this one your best shot.",
    ],
    "general_motivation": [
        "Every 'no' brings you closer to a 'yes'.",
        "Job searching is tough, but you're tougher.",
        "Your next opportunity is out there. Keep going!",
        "Remember: every successful person was once a job seeker.",
        "Take it one application at a time. You're doing great.",
    ],
}

WELLNESS_TIPS = [
    "Take a 5-minute break after every 5 applications.",
    "Quality over quantity - a tailored application beats 10 generic ones.",
    "Step away from the screen and take a short walk.",
    "Celebrate small wins - every application sent is progress.",
    "Connect with a friend or mentor to talk about your job search.",
    "Exercise can help reduce job search stress - even a 10-minute walk helps.",
    "Set boundaries - don't job search after 8 PM.",
    "Review your accomplishments - you've achieved more than you remember.",
    "Focus on what you can control: your applications, not the outcomes.",
    "Rejection isn't personal - companies reject great candidates all the time.",
]

BREAK_REMINDERS = [
    "You've been at it for a while. Time for a 5-minute breather?",
    "Your eyes and mind need a rest. Step away for a moment.",
    "Break time! A refreshed mind writes better applications.",
    "Productivity tip: short breaks improve focus. Take one now!",
    "You're working hard! Reward yourself with a quick break.",
]
