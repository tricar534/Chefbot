import time
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from recommender import search_recipes_by_ingredients, filter_by_diet # pyright: ignore[reportMissingImports]

# ----------------------------
# Helper function: simulate bot response
# ----------------------------
def get_response_from_recommender(query: str, max_results: int = 5, diet_restrictions=None):
    """
    Simulate chatbot response using recommender.py
    Args:
        query: user query string, assumed to be a list of ingredients separated by commas
        max_results: max recipes to return
        diet_restrictions: optional list of dietary restrictions
    Returns:
        List of recipe dictionaries
    """
    # Extract ingredients from query (split by commas)
    ingredients = [i.strip() for i in query.split(',') if i.strip()]
    if not ingredients:
        return []

    # Get recipes
    recipes = search_recipes_by_ingredients(ingredients, max_results=max_results*2)
    
    # Apply diet filter if specified
    if diet_restrictions:
        recipes = filter_by_diet(recipes, diet_restrictions)

    # Limit to max_results
    return recipes[:max_results]

# ----------------------------
# Sample test queries
# ----------------------------
test_queries = [
    # Simple ingredient searches
    {"query": "chicken, rice", "diet_restrictions": None},
    {"query": "pasta, tomato", "diet_restrictions": None},
    {"query": "tofu, broccoli", "diet_restrictions": None},
    {"query": "beef, potato", "diet_restrictions": None},
    {"query": "salmon, lemon, garlic", "diet_restrictions": None},

    # Diet-only searches
    {"query": "", "diet_restrictions": ["vegetarian"]},
    {"query": "", "diet_restrictions": ["vegan"]},
    {"query": "", "diet_restrictions": ["keto"]},

    # Combined diet + ingredients
    {"query": "tofu, broccoli", "diet_restrictions": ["vegetarian"]},
    {"query": "lettuce, tomato, cucumber", "diet_restrictions": ["vegan"]},
    {"query": "chicken, spinach, cheese", "diet_restrictions": ["keto"]},

    # Fruit / dessert search (safe/common)
    {"query": "banana, apple, strawberry", "diet_restrictions": None},

    # Breakfast / simple recipes
    {"query": "eggs, milk, bread", "diet_restrictions": None},
    {"query": "oats, milk, honey", "diet_restrictions": None},

    {"query": "chicken, rice", "diet_restrictions": None}, 
    {"query": "pasta, tomato", "diet_restrictions": None}, 
    {"query": "tofu, broccoli", "diet_restrictions": ["vegetarian"]}, 
    {"query": "lettuce, tomato, cucumber", "diet_restrictions": ["vegan"]}, 
    {"query": "banana, apple, strawberry, chocolate, kiwi ", "diet_restrictions": None}, 
    {"query": "eggs, milk, bread, chicken, cheese, flour", "diet_restrictions": None}, 
    {"query": "tomato, potato, lettuce, broccoli, milk, bread", "diet_restrictions": ["vegetarian"]},

]

# ----------------------------
# Evaluation function
# ----------------------------
def evaluate_recommender(test_queries, max_results=5):
    results = []

    for t in test_queries:
        query = t["query"]
        diet_restrictions = t.get("diet_restrictions", None)

        start_time = time.time()

        # Get recommendations
        recommended_recipes = get_response_from_recommender(query, max_results=max_results, diet_restrictions=diet_restrictions)
        response_time = (time.time() - start_time) * 1000  # milliseconds
        

        # Coverage: at least one recipe returned
        coverage = int(len(recommended_recipes) > 0)

        # Constraint satisfaction
        if diet_restrictions:
            valid_recipes = filter_by_diet(recommended_recipes, diet_restrictions)
            constraint_satisfaction = len(valid_recipes) / len(recommended_recipes) if recommended_recipes else 0
        else:
            constraint_satisfaction = None

        # Relevance: ingredient overlap score
        ingredients = [i.strip().lower() for i in query.split(',') if i.strip()]
        relevance_scores = []
        for recipe in recommended_recipes:
            recipe_ingredients = recipe.get('ingredients', '').lower()
            matches = sum(1 for ing in ingredients if ing in recipe_ingredients)
            score = matches / len(ingredients) if ingredients else 0
            relevance_scores.append(score)
        avg_relevance = sum(relevance_scores)/len(relevance_scores) if relevance_scores else 0

        results.append({
            "query": query,
            "diet_restrictions": ", ".join(diet_restrictions) if diet_restrictions else "None",
            "num_recipes": len(recommended_recipes),
            "coverage": coverage,
            "constraint_satisfaction": constraint_satisfaction,
            "avg_relevance": avg_relevance,
            "response_time": response_time
        })

    df_results = pd.DataFrame(results)
    return df_results

# ----------------------------
# Aggregate metrics
# ----------------------------
def compute_metrics(df):
    metrics = {
        "Average Coverage (%)": df["coverage"].mean() * 100,
        "Average Constraint Satisfaction (%)": df["constraint_satisfaction"].dropna().mean() * 100 if df["constraint_satisfaction"].notna().any() else None,
        "Average Relevance": df["avg_relevance"].mean(),
        "Average Response Time (ms)": df["response_time"].mean()
    }
    return metrics

# ----------------------------
# Main execution
# ----------------------------
if __name__ == "__main__":
    print("Running evaluation on test queries...\n")
    df = evaluate_recommender(test_queries)
    print(df)
    
    metrics = compute_metrics(df)
    print("\nOverall Metrics:")
    for k, v in metrics.items():
        if v is not None:
            print(f"{k}: {v:.2f}")
        else:
            print(f"{k}: N/A")