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

# Extract key diet restriction words 
def extract_diet_restrictions(user_input):
    
    text_lower = user_input.lower()
    found = []

    for known in DIET_KEYWORDS:
        if known in text_lower:
            found.append(known.replace(" ", "_"))

    return found

if __name__ == "__main__":
    test_messages = [
        "hello there",
        "plan my meals",
        "make a meal plan high protein",
        "I want low carb and keto recipes",
        "vegan please",
        "what can I cook?"
    ]

    print("=== REGEX MATCH TESTS ===")
    for msg in test_messages:
        print(f"\nMessage: {msg}")
        print(" greeting match:", bool(GREETING_PATTERN.search(msg)))
        print(" ingredient match:", bool(INGREDIENT_PATTERN.search(msg)))
        print(" meal plan match:", bool(MEAL_PLAN_PATTERN.search(msg)))
        print(" diet match:", bool(DIET_PATTERN.search(msg)))

    print("\n=== DIET EXTRACTION TESTS ===")
    print(extract_diet_restrictions("I want low carb and keto recipes"))
    print(extract_diet_restrictions("High protein please"))
    print(extract_diet_restrictions("No restrictions"))
