"""
Prints
- Intent classification accuracy
- Recipe relevance (>= 80% ingredient match)
- Average backend response time

"""
import time
from typing import List

# =====================
# IMPORT  MODULES
# =====================

# Intent detection + labels

from intents import (
        determine_intent,  # function: (message: str) -> dict with key "intent"
        INTENT_GREETING,
        INTENT_INGREDIENT,
        INTENT_MEAL_PLAN,
        INTENT_DIET,
        INTENT_RECIPE_DETAIL,
        INTENT_CLEAR_DIET,
        INTENT_OTHER,
    )

from recommender import search_recipes_by_ingredients  

# =====================
# 1) INTENT ACCURACY
# =====================

# Small labeled dataset of test messages
INTENT_TESTS = [
    # random test
    {"msg": "what can i cook with chicken and rice", "expected": INTENT_INGREDIENT},
    {"msg": "i have chicken and rice", "expected": INTENT_INGREDIENT},
    {"msg": "make me a healthy meal plan for the week", "expected": INTENT_MEAL_PLAN},
    {"msg": "i am vegetarian and allergic to peanuts", "expected": INTENT_DIET},
    {"msg": "show me details for recipe 5", "expected": INTENT_RECIPE_DETAIL},
    {"msg": "show me recipe 5", "expected": INTENT_RECIPE_DETAIL},
    {"msg": "5", "expected": INTENT_RECIPE_DETAIL},
    {"msg": "clear my diet preferences", "expected": INTENT_CLEAR_DIET},
    {"msg": "clear my diet ", "expected": INTENT_CLEAR_DIET},
    {"msg": "what's the weather today", "expected": INTENT_OTHER},

    # Greetings
    {"msg": "hi", "expected": INTENT_GREETING},
    {"msg": "hello there", "expected": INTENT_GREETING},
    {"msg": "hey chefbot", "expected": INTENT_GREETING},

    # NEW FORMAT: "I want a [diet] with [ingredients]"
    # (I’m treating these as diet_restrictions; change to INTENT_INGREDIENT if your logic does that)
    {"msg": "I want a vegan meal with rice", "expected": INTENT_DIET},
    {"msg": "I want a vegetarian with pasta and tomatoes", "expected": INTENT_DIET},
    {"msg": "I want a keto recipe with chicken and broccoli", "expected": INTENT_DIET},
    {"msg": "I want vegan with tofu and spinach", "expected": INTENT_DIET},
    {"msg": "I want a low carb with eggs and cheese", "expected": INTENT_DIET},

    # Ingredient intent tests
    {"msg": "I have chicken, rice and eggs", "expected": INTENT_INGREDIENT},
    {"msg": "i have pasta and tomato sauce", "expected": INTENT_INGREDIENT},
    {"msg": "I have bread, peanut butter & banana", "expected": INTENT_INGREDIENT},
    {"msg": "ihave tuna and mayo", "expected": INTENT_INGREDIENT},
    {"msg": "  I   have   chicken,   rice and eggs  ", "expected": INTENT_INGREDIENT},

    # Meal plan tests
    {"msg": "meal plan", "expected": INTENT_MEAL_PLAN},
    {"msg": "plan my meals", "expected": INTENT_MEAL_PLAN},
    {"msg": "make a meal plan", "expected": INTENT_MEAL_PLAN},
    {"msg": "make a meal plan high protein", "expected": INTENT_MEAL_PLAN},
    {"msg": "plan my meals low carb", "expected": INTENT_MEAL_PLAN},

    # Diet tests
    {"msg": "vegan please", "expected": INTENT_DIET},
    {"msg": "vegetarian recipes", "expected": INTENT_DIET},
    {"msg": "low carb ideas", "expected": INTENT_DIET},
    {"msg": "high protein meals", "expected": INTENT_DIET},
    {"msg": "keto options", "expected": INTENT_DIET},

    # Unknown / general suggestions
    {"msg": "what can I cook?", "expected": INTENT_OTHER},
    {"msg": "suggest something tasty", "expected": INTENT_OTHER},
    {"msg": "I am hungry", "expected": INTENT_OTHER},

    # Close / mixed cases
    {"msg": "I have", "expected": INTENT_OTHER},  # not enough info
    {"msg": "I want a meal plan and I have chicken", "expected": INTENT_MEAL_PLAN},
    {"msg": "hello I have eggs", "expected": INTENT_INGREDIENT},
]

def test_intent_accuracy() -> None:
    """Evaluate how often determine_intent gets the right label.

    determine_intent returns a dict like:
    {"intent": ..., "ingredients": [...], ...}
    We only compare the "intent" field to the expected label.
    """

    if determine_intent is None:
        print("[SKIP] determine_intent could not be imported. Check intents.py import.")
        return

    total = len(INTENT_TESTS)
    correct = 0

    print("Running intent accuracy test on", total, "queries...")

    for case in INTENT_TESTS:
        result = determine_intent(case["msg"])
        # result is a dict; pull out just the label string
        predicted = result.get("intent")
        if predicted == case["expected"]:
            correct += 1
        else:
            print(
                f"  [INTENT] WRONG for '{case['msg']}' -> got '{result}', expected '{case['expected']}'"
            )

    accuracy = (correct / total * 100) if total > 0 else 0.0
    print(f"Intent Accuracy = {accuracy:.1f}% ({correct}/{total})")


# =====================
# 2) RECIPE RELEVANCE
# =====================

def _normalize_ingredients(ings: List[str]) -> List[str]:
    return [i.lower().strip() for i in ings if i.strip()]


def _match_ratio(user_ings: List[str], recipe_ings: List[str]) -> float:
    """Compute fraction of user ingredients that appear in the recipe.

    This is intentionally simple: we treat it as bag-of-words.
    """

    user = _normalize_ingredients(user_ings)

    if isinstance(recipe_ings, list):
        recipe_text = " ".join(recipe_ings).lower()
    else:
        recipe_text = str(recipe_ings).lower()

    if not user:
        return 0.0

    matches = sum(1 for ing in user if ing in recipe_text)
    return matches / len(user)


# For relevance, we can reuse real user messages that should trigger
# INTENT_INGREDIENT and let determine_intent extract ingredients.
RELEVANCE_TEST_CASES = [ case for case in INTENT_TESTS if case["expected"] == INTENT_INGREDIENT ]


def test_recipe_relevance(threshold: float = 0.8, max_recipes: int = 5) -> None:
    """Measure % of recipes with >= threshold ingredient match.

    Uses determine_intent(msg) to get the ingredients list, then checks how
    well the recommended recipes match those ingredients.
    """

    if search_recipes_by_ingredients is None:
        print(
            "[SKIP] search_recipes_by_ingredients could not be imported. "
        )
        return

    total_recipes = 0
    relevant_recipes = 0

    print("Running recipe relevance test...")

    for case in RELEVANCE_TEST_CASES:
        intent_result = determine_intent(case["msg"])
        user_ings = intent_result.get("ingredients", [])

        # skip if we didn't actually extract any ingredients
        if not user_ings:
            continue

        recipes = search_recipes_by_ingredients(user_ings) or []  # type: ignore
        recipes = recipes[:max_recipes]

        for r in recipes:
            recipe_ings = r.get("ingredients") or r.get("Ingredients")
            ratio = _match_ratio(user_ings, recipe_ings)
            total_recipes += 1
            if ratio >= threshold:
                relevant_recipes += 1

    if total_recipes == 0:
        print("No recipes returned in relevance tests. Check search_recipes_by_ingredients.")
        return

    relevance = relevant_recipes / total_recipes * 100
    print(
        f"Recipe Relevance = {relevance:.1f}% "
        f"({relevant_recipes}/{total_recipes} recipes with >= {threshold*100:.0f}% ingredient match)"
    )


# =====================
# 3) PERFORMANCE / RESPONSE TIME
# =====================


def test_performance(num_runs: int = 20) -> None:
    """Measure average time for search_recipes_by_ingredients calls."""

    if search_recipes_by_ingredients is None:
        print(
            "[SKIP] search_recipes_by_ingredients could not be imported. "
        )
        return

    print(f"Running performance test over {num_runs} runs...")

    start = time.perf_counter()

    for _ in range(num_runs):
        # Simple fixed query – adjust ingredients if you want
        search_recipes_by_ingredients(["chicken", "rice", "eggs", "bread", "squash", "broccoli", ])  # type: ignore

    end = time.perf_counter()

    avg_seconds = (end - start) / num_runs if num_runs > 0 else 0.0
    print(f"Average backend response time ≈ {avg_seconds*1000:.1f} ms per call")


# =====================
# MAIN
# =====================

if __name__ == "__main__":
    print("=== Intent Accuracy Test ===")
    test_intent_accuracy()

    print("=== Recipe Relevance Test ===")
    test_recipe_relevance()

    print("=== Performance Test ===")
    test_performance()
