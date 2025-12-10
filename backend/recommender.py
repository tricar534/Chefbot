import sqlite3
import os
from typing import List, Dict, Optional

# Path to the SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', '5k-recipes.db')

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn


def search_recipes_by_ingredients(
    ingredients: List[str], 
    max_results: int = 20  # Increased from 5 to 20 for better filtering
) -> List[Dict]:
    """
    Search for recipes that match the given ingredients.
    
    Args:
        ingredients: List of ingredient names to search for
        max_results: Maximum number of recipes to return
    
    Returns:
        List of matching recipe dictionaries
    """
    if not ingredients:
        return []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build SQL query to search for recipes containing any of the ingredients
        # Using LIKE for partial matching
        conditions = []
        params = []
        
        for ingredient in ingredients:
            conditions.append("LOWER(Ingredients) LIKE ?")
            params.append(f"%{ingredient.lower()}%")
        
        # Combine conditions with OR
        where_clause = " OR ".join(conditions)
        
        query = f"""
            SELECT id, Title, Ingredients, Instructions
            FROM recipes
            WHERE {where_clause}
            LIMIT ?
        """
        params.append(max_results * 3)  # Get 3x more results to allow for filtering
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries and calculate match scores
        recipes = []
        for row in rows:
            recipe = {
                'id': row['id'],
                'title': row['Title'],
                'ingredients': row['Ingredients'],
                'instructions': row['Instructions']
            }
            
            # Count how many search ingredients match
            ingredients_lower = row['Ingredients'].lower()
            matches = sum(1 for ing in ingredients if ing.lower() in ingredients_lower)
            recipe['match_count'] = matches
            
            recipes.append(recipe)
        
        # Sort by match count (descending)
        recipes.sort(key=lambda x: x['match_count'], reverse=True)
        
        return recipes[:max_results]  # Return only max_results after sorting
    
    finally:
        conn.close()


def filter_by_diet(recipes: List[Dict], diet_restrictions: List[str]) -> List[Dict]:
    """
    Filter recipes by diet restrictions.
    
    Args:
        recipes: List of recipe dictionaries
        diet_restrictions: List of diet restriction strings
    
    Returns:
        Filtered list of recipes
    """
    if not diet_restrictions:
        return recipes
    
    filtered = []
    
    # Expanded meat keywords for vegetarian/vegan
    meat_keywords = [
        'chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'goose',
        'meat', 'bacon', 'sausage', 'ham', 'prosciutto', 'salami',
        'fish', 'salmon', 'tuna', 'cod', 'shrimp', 'crab', 'lobster',
        'anchovy', 'sardine', 'trout', 'tilapia', 'halibut',
        'steak', 'ribs', 'chop', 'cutlet', 'ground beef', 'ground pork',
        'pepperoni', 'chorizo', 'veal', 'venison', 'bison'
    ]
    
    # Animal products for vegan
    animal_keywords = [
        'milk', 'cheese', 'butter', 'egg', 'cream', 'yogurt', 'honey',
        'whey', 'casein', 'lactose', 'ghee', 'buttermilk', 'sour cream',
        'mayonnaise', 'mayo', 'gelatin', 'lard'
    ]
    
    # High carb foods for keto
    high_carb = [
        'bread', 'pasta', 'rice', 'potato', 'flour', 'sugar',
        'noodle', 'tortilla', 'bagel', 'cereal', 'oat', 'quinoa',
        'corn', 'wheat', 'barley', 'couscous'
    ]
    
    for recipe in recipes:
        # Check ingredients, title, and instructions
        recipe_text = (
            recipe.get('ingredients', '') + ' ' + 
            recipe.get('title', '') + ' ' +
            recipe.get('instructions', '')
        ).lower()
        
        is_valid = True
        
        for diet in diet_restrictions:
            diet_lower = diet.lower().replace('_', ' ')
            
            # Check for vegetarian (no meat)
            if 'vegetarian' in diet_lower:
                if any(meat in recipe_text for meat in meat_keywords):
                    is_valid = False
                    break
            
            # Check for vegan (no meat AND no animal products)
            if 'vegan' in diet_lower:
                # Check for meat
                if any(meat in recipe_text for meat in meat_keywords):
                    is_valid = False
                    break
                # Check for animal products
                if any(animal in recipe_text for animal in animal_keywords):
                    is_valid = False
                    break
            
            # Check for keto/low carb (ONLY apply this if keto/low carb is specified)
            if 'keto' in diet_lower or 'low_carb' in diet_lower or 'low carb' in diet_lower:
                if any(carb in recipe_text for carb in high_carb):
                    is_valid = False
                    break
        
        if is_valid:
            filtered.append(recipe)
    
    return filtered


def get_recipe_by_id(recipe_id: int) -> Optional[Dict]:
    """
    Get a specific recipe by ID.
    
    Args:
        recipe_id: Recipe database ID
    
    Returns:
        Recipe dictionary or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, Title, Ingredients, Instructions
            FROM recipes
            WHERE id = ?
        """, (recipe_id,))
        
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'title': row['Title'],
                'ingredients': row['Ingredients'],
                'instructions': row['Instructions']
            }
        return None
    
    finally:
        conn.close()


def format_recipe_response(recipes: List[Dict], searched_ingredients: List[str]) -> str:
    """
    Format recipe search results into a readable string.
    
    Args:
        recipes: List of recipe dictionaries
        searched_ingredients: The ingredients that were searched for
    
    Returns:
        Formatted string with recipe information
    """
    if not recipes:
        return (
            f"Sorry, I couldn't find any recipes matching your criteria with {', '.join(searched_ingredients)}.\n\n"
            f"💡 Try:\n"
            f"• Using different ingredients\n"
            f"• Removing diet restrictions\n"
            f"• Being more general (e.g., 'vegetables' instead of specific veggies)"
        )
    
    response_lines = [f"🍳 Found {len(recipes)} recipe(s) for you:\n"]
    
    for i, recipe in enumerate(recipes, 1):
        title = recipe.get('title', 'Unknown Recipe')
        match_count = recipe.get('match_count', 0)
        
        # Get first few ingredients for preview
        ingredients = recipe.get('ingredients', '')
        ingredients_list = ingredients.split('\n')[:3]  # Show first 3 ingredients
        ingredients_preview = ', '.join([ing.strip() for ing in ingredients_list if ing.strip()])
        
        response_lines.append(
            f"{i}. 📝 {title}\n"
            f"   ✓ Matches {match_count}/{len(searched_ingredients)} of your ingredients\n"
            f"   🛒 Preview: {ingredients_preview}...\n"
            f"   {'─' * 50}"  # Add separator line
        )
    
    response_lines.append("\n💡 Reply with the recipe number (e.g., '1') to see full details!")
    
    return "\n".join(response_lines)


def format_recipe_details(recipe: Dict) -> str:
    """
    Format detailed recipe information.
    
    Args:
        recipe: Recipe dictionary
    
    Returns:
        Formatted string with full recipe details
    """
    title = recipe.get('title', 'Unknown Recipe')
    ingredients = recipe.get('ingredients', 'No ingredients listed')
    instructions = recipe.get('instructions', 'No instructions available')
    
    # Format ingredients (split by newlines if they exist)
    ingredients_lines = ingredients.strip().split('\n')
    ingredients_text = "\n".join([f"   • {ing.strip()}" for ing in ingredients_lines if ing.strip()])
    
    # Format instructions (split by periods or newlines)
    if '\n' in instructions:
        instruction_lines = instructions.strip().split('\n')
    else:
        instruction_lines = instructions.strip().split('. ')
    
    instructions_text = "\n".join([
        f"   {i+1}. {step.strip()}" 
        for i, step in enumerate(instruction_lines) 
        if step.strip()
    ])
    
    response = (
        f"📝 {title}\n\n"
        f"🛒 Ingredients:\n{ingredients_text}\n\n"
        f"👨‍🍳 Instructions:\n{instructions_text}"
    )
    
    return response


def get_recipe_count() -> int:
    """Get total number of recipes in database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM recipes")
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()