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

# --------Helper functions-----------

# Extract key diet restriction words 
# EX: Turns "LoW CaRb" -> "low_carb"
def extract_diet_restrictions(user_input):
    
    text_lower = user_input.lower()
    found = []

    for known in DIET_KEYWORDS:
        if known in text_lower:
            found.append(known.replace(" ", "_"))

    return found

# Extract ingredients and puts into list
# EX: "chicken, rice and eggs" -> [ "chicken", "rice", "eggs"]
def extract_ingredients(user_ingredients):
    
    if not user_ingredients:
        return []
    
    split = re.split(r",| and | & ", user_ingredients, flags=re.IGNORECASE)
    ingredients = []

    for parts in split:
        item = parts.strip().lower()
        if item:
            ingredients.append(item)

    return ingredients
# ------------------------------------

# Uses regex rules to identify intent (ingredients, diet restrictions )
def determine_intent(user_input):

    result =  {
                "intent": INTENT_OTHER,
                "ingredients": [],
                "diet_restrictions": [],
                "user_input": user_input
              }

    # If user input empty
    if not user_input:
        return result
    
    # Clean up input
    clean_text = user_input.strip()
    text_lower = clean_text.lower()
    
    # Store cleaned up text
    result["user_input"] = clean_text
    
    
    # Find diet restictions
    result["diet_restrictions"] = extract_diet_restrictions(text_lower)
    
    # Detect greeting
    if GREETING_PATTERN.search(text_lower):
        result["intent"] = INTENT_GREETING
        return result
    
    # Detect meal plan 
    if MEAL_PLAN_PATTERN.search(text_lower):
        result["intent"] = INTENT_MEAL_PLAN
        return result
   
    # Gather all that was captured by INGREDIENT_PATTERN
    found_ingredient = INGREDIENT_PATTERN.search(text_lower) 
    
    # Detect ingredient search
    if found_ingredient:
        result["intent"] = INTENT_INGREDIENT
        captured = found_ingredient.group(1)
        result["ingredients"] = extract_ingredients(captured)
        return result
    
    # Detect diet
    if DIET_PATTERN.search(text_lower):
        result["intent"] = INTENT_DIET
        return result
    

    # Unknown intent
    return result


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
