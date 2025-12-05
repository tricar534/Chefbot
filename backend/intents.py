import re

# Intent labels
INTENT_GREETING = "greeting"
INTENT_INGREDIENT = "ingredient_search"
INTENT_MEAL_PLAN = "meal_plan"
INTENT_DIET = "diet_restrictions"
INTENT_OTHER = "unknown_intent"

# Simple regex patterns

GREETING_PATTERN = re.compile(r"\b(hi|hello|hey)\b", re.IGNORECASE)

INGREDIENT_PATTERN = re.compile(r"\bi\s*have\s+(.+)", re.IGNORECASE)

MEAL_PLAN_PATTERN = re.compile(r"\b(meal plan|plan my meal|plan my meals|make a meal plan)\b", re.IGNORECASE)

DIET_PATTERN = re.compile(r"\b(vegetarian|vegan|high protein|low carb|keto)\b", re.IGNORECASE)

DIET_KEYWORDS = ["vegetarian", "vegan", "high protein", "low carb", "keto"]




