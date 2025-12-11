import re

# Intent labels
INTENT_GREETING = "greeting"
INTENT_INGREDIENT = "ingredient_search"
INTENT_MEAL_PLAN = "meal_plan"
INTENT_DIET = "diet_restrictions"
INTENT_RECIPE_DETAIL = "recipe_detail"
INTENT_CLEAR_DIET = "clear_diet"
INTENT_OTHER = "unknown_intent"

# Simple regex patterns

GREETING_PATTERN = re.compile(r"\b(hi|hello|hey)\b", re.IGNORECASE)
INGREDIENT_PATTERN = re.compile(r"\bi\s*have\s+(.+)", re.IGNORECASE)
# New pattern: "I want a [diet] with [ingredients]"
DIET_WITH_INGREDIENTS_PATTERN = re.compile(
    r"\bi\s*want\s+(?:a|an)?\s*(vegetarian|vegan|high protein|low carb|keto|ketogenic)\s+(?:meal|recipe|dish)?\s*with\s+(.+)", 
    re.IGNORECASE
)
MEAL_PLAN_PATTERN = re.compile(r"\b(meal plan|plan my meal|plan my meals|make a meal plan)\b", re.IGNORECASE)
DIET_PATTERN = re.compile(r"\b(vegetarian|vegan|high protein|low carb|keto)\b", re.IGNORECASE)
# Pattern to detect recipe number requests: "1", "recipe 1", "show me 2", etc.
RECIPE_NUMBER_PATTERN = re.compile(r"^(?:recipe\s+)?(\d+)$|^(?:show\s+(?:me\s+)?)?(\d+)$", re.IGNORECASE)
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
                "recipe_number": None,
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

    # Check for recipe number request (e.g., "1", "recipe 2", "show me 3")
    recipe_num_match = RECIPE_NUMBER_PATTERN.search(clean_text)
    if recipe_num_match:
        # Get the number from whichever group matched
        number = recipe_num_match.group(1) or recipe_num_match.group(2)
        result["recipe_number"] = int(number)
        result["intent"] = INTENT_RECIPE_DETAIL
        return result

    # Find diet restrictions (general extraction)
    result["diet_restrictions"] = extract_diet_restrictions(text_lower)
    
    # Check for "I want a [diet] with [ingredients]" pattern FIRST
    diet_with_ingredients = DIET_WITH_INGREDIENTS_PATTERN.search(text_lower)
    
    if diet_with_ingredients:
        # Extract diet type
        diet_type = diet_with_ingredients.group(1).strip()
        result["diet_restrictions"] = [diet_type.replace(" ", "_")]
        
        # Extract ingredients after "with"
        ingredients_part = diet_with_ingredients.group(2).strip()
        result["ingredients"] = extract_ingredients(ingredients_part)
        result["intent"] = INTENT_INGREDIENT
        return result
    
    # Gather all that was captured by INGREDIENT_PATTERN
    found_ingredient = INGREDIENT_PATTERN.search(text_lower) 

    # Capture ingredient if found
    if found_ingredient:
        captured = found_ingredient.group(1)
        result["ingredients"] = extract_ingredients(captured)

    # Detect greeting
    if GREETING_PATTERN.search(text_lower):
        result["intent"] = INTENT_GREETING
        return result
    
    # Detect meal plan 
    if MEAL_PLAN_PATTERN.search(text_lower):
        result["intent"] = INTENT_MEAL_PLAN
        return result
    
    # Detect ingredient search
    if found_ingredient:
        result["intent"] = INTENT_INGREDIENT
        return result
    
    # Detect diet
    if DIET_PATTERN.search(text_lower):
        result["intent"] = INTENT_DIET
        return result
    

    # Unknown intent
    return result


# ------------------ TESTING ------------------
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("INTENT SUMMARY")
    print("=" * 50)

    test_messages = [
        "",

        # Greetings
        "hi",
        "hello there",
        "hey chefbot",

        # NEW FORMAT: "I want a [diet] with [ingredients]"
        "I want a vegan meal with rice",
        "I want a vegetarian with pasta and tomatoes",
        "I want a keto recipe with chicken and broccoli",
        "I want vegan with tofu and spinach",
        "I want a low carb with eggs and cheese",

        # Ingredient intent test
        "I have chicken, rice and eggs",
        "i have pasta and tomato sauce",
        "I have bread, peanut butter & banana",
        "ihave tuna and mayo",
        "  I   have   chicken,   rice and eggs  ",

        # Meal plan test
        "meal plan",
        "plan my meals",
        "make a meal plan",
        "make a meal plan high protein",
        "plan my meals low carb",

        # Diet test
        "vegan please",
        "vegetarian recipes",
        "low carb ideas",
        "high protein meals",
        "keto options",

        # Unknown
        "what can I cook?",
        "suggest something tasty",
        "I am hungry",

        # Close case
        "I have",
        "I want a meal plan and I have chicken",
        "hello I have eggs",
    ]


    for msg in test_messages:
        out = determine_intent(msg)
        intent = out["intent"]
        ingredients = ", ".join(out["ingredients"]) if out["ingredients"] else "-"
        diets = ", ".join(out["diet_restrictions"]) if out["diet_restrictions"] else "-"

        print(f"Input: {msg}")
        print(f"  Intent: {intent} | Ingredients: {ingredients} | Diet: {diets}\n")
# ---------------------------------------------