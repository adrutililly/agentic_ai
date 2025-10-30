# tools_langchain.py
"""
Simple tool definitions for agentic AI without LangChain dependencies.
"""
import logging
import wikipedia
import ast
import operator
from typing import Callable

log = logging.getLogger("tools_langchain")

class SimpleTool:
    """Simple tool wrapper that the LLM can use."""
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
    
    def __repr__(self):
        return f"Tool(name='{self.name}')"

# ============================================================================
# WIKIPEDIA TOOL
# ============================================================================

def wikipedia_search_function(query: str) -> str:
    """Search Wikipedia and return a summary."""
    try:
        log.info(f"🔍 Wikipedia searching: '{query}'")
        print(f"📚 Wikipedia Tool: Searching for '{query}'")
        
        # Clean query
        clean_query = query.strip().rstrip('?!.,;:').strip()
        
        # Try direct lookup
        try:
            page = wikipedia.page(clean_query, auto_suggest=False)
        except:
            page = wikipedia.page(clean_query, auto_suggest=True)
        
        result = f"**{page.title}**\n\n{page.summary}\n\nSource: {page.url}"
        log.info(f"✅ Found: {page.title}")
        print(f"✅ Wikipedia Tool: Found '{page.title}'\n")
        return result
        
    except wikipedia.DisambiguationError as e:
        try:
            page = wikipedia.page(e.options[0])
            return f"**{page.title}**\n\n{page.summary}\n\nSource: {page.url}"
        except:
            return f"Found multiple results. Please be more specific. Options: {', '.join(e.options[:5])}"
    
    except wikipedia.PageError:
        try:
            results = wikipedia.search(clean_query, results=3)
            if results:
                page = wikipedia.page(results[0])
                return f"**{page.title}**\n\n{page.summary}\n\nSource: {page.url}"
            return f"No Wikipedia page found for '{clean_query}'. Try different keywords."
        except:
            return f"Could not find information about '{clean_query}' on Wikipedia."
    
    except Exception as e:
        log.error(f"Wikipedia error: {e}")
        return f"Error searching Wikipedia: {str(e)}"

# ============================================================================
# CALCULATOR TOOL
# ============================================================================

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

def safe_eval_expression(expression: str) -> float:
    """Safely evaluate a mathematical expression using AST."""
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            op = SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operation: {type(node.op).__name__}")
            return op(_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operation: {type(node.op).__name__}")
            return op(_eval(node.operand))
        else:
            raise ValueError(f"Unsupported expression: {type(node).__name__}")
    
    tree = ast.parse(expression, mode='eval')
    return _eval(tree.body)

def calculator_function(expression: str) -> str:
    """Perform mathematical calculations."""
    try:
        log.info(f"🔢 Calculating: '{expression}'")
        print(f"🔢 Calculator Tool: Evaluating '{expression}'")
        
        # Clean expression
        clean = expression.strip()
        clean = clean.replace(" plus ", "+")
        clean = clean.replace(" minus ", "-")
        clean = clean.replace(" times ", "*")
        clean = clean.replace(" divided by ", "/")
        clean = clean.replace(" to the power of ", "**")
        clean = clean.replace("x", "*").replace("×", "*").replace("÷", "/")
        clean = clean.replace(" ", "")
        
        result = safe_eval_expression(clean)
        
        # Format nicely
        if result == int(result):
            result = int(result)
        
        log.info(f"✅ Result: {result}")
        print(f"✅ Calculator Tool: Result = {result}\n")
        return f"The result is: **{result}**"
        
    except Exception as e:
        error_msg = f"Cannot calculate '{expression}'. Error: {str(e)}"
        log.error(error_msg)
        print(f"❌ Calculator Tool: {error_msg}\n")
        return error_msg

# ============================================================================
# UNIT CONVERTER TOOL
# ============================================================================

UNIT_CONVERSIONS = {
    "length": {
        "meters": 1, "m": 1, "meter": 1,
        "kilometers": 1000, "km": 1000, "kilometer": 1000,
        "centimeters": 0.01, "cm": 0.01, "centimeter": 0.01,
        "millimeters": 0.001, "mm": 0.001, "millimeter": 0.001,
        "miles": 1609.34, "mile": 1609.34, "mi": 1609.34,
        "yards": 0.9144, "yard": 0.9144, "yd": 0.9144,
        "feet": 0.3048, "foot": 0.3048, "ft": 0.3048,
        "inches": 0.0254, "inch": 0.0254, "in": 0.0254,
    },
    "weight": {
        "kilograms": 1, "kg": 1, "kilogram": 1,
        "grams": 0.001, "g": 0.001, "gram": 0.001,
        "milligrams": 0.000001, "mg": 0.000001, "milligram": 0.000001,
        "pounds": 0.453592, "pound": 0.453592, "lb": 0.453592, "lbs": 0.453592,
        "ounces": 0.0283495, "ounce": 0.0283495, "oz": 0.0283495,
        "tons": 1000, "ton": 1000,
    },
    "temperature": {
        "celsius": "C", "c": "C",
        "fahrenheit": "F", "f": "F",
        "kelvin": "K", "k": "K",
    },
    "volume": {
        "liters": 1, "l": 1, "liter": 1,
        "milliliters": 0.001, "ml": 0.001, "milliliter": 0.001,
        "gallons": 3.78541, "gallon": 3.78541, "gal": 3.78541,
        "quarts": 0.946353, "quart": 0.946353, "qt": 0.946353,
        "pints": 0.473176, "pint": 0.473176, "pt": 0.473176,
        "cups": 0.236588, "cup": 0.236588,
    }
}

def find_unit_category(unit: str):
    """Find category for a unit."""
    unit_lower = unit.lower()
    for category, units in UNIT_CONVERSIONS.items():
        if unit_lower in units:
            return category
    return None

def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between C, F, and K."""
    from_u = UNIT_CONVERSIONS["temperature"].get(from_unit.lower())
    to_u = UNIT_CONVERSIONS["temperature"].get(to_unit.lower())
    
    # To Celsius first
    if from_u == "C":
        celsius = value
    elif from_u == "F":
        celsius = (value - 32) * 5/9
    elif from_u == "K":
        celsius = value - 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {from_unit}")
    
    # From Celsius to target
    if to_u == "C":
        return celsius
    elif to_u == "F":
        return celsius * 9/5 + 32
    elif to_u == "K":
        return celsius + 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {to_unit}")

def unit_converter_function(conversion_query: str) -> str:
    """Convert between units."""
    try:
        log.info(f"🔄 Converting: '{conversion_query}'")
        print(f"🔄 Converter Tool: Processing '{conversion_query}'")
        
        # Parse the query
        import re
        pattern = r'(?:convert\s+)?(\d+\.?\d*)\s+(\w+)\s+(?:to|in)\s+(\w+)'
        match = re.search(pattern, conversion_query.lower())
        
        if not match:
            return "Please use format: 'X unit to unit' (e.g., '100 kilometers to miles')"
        
        value = float(match.group(1))
        from_unit = match.group(2)
        to_unit = match.group(3)
        
        from_cat = find_unit_category(from_unit)
        to_cat = find_unit_category(to_unit)
        
        if not from_cat or not to_cat:
            return f"Unknown unit: {from_unit if not from_cat else to_unit}"
        
        if from_cat != to_cat:
            return f"Cannot convert between {from_cat} and {to_cat}"
        
        # Convert
        if from_cat == "temperature":
            result = convert_temperature(value, from_unit, to_unit)
        else:
            from_factor = UNIT_CONVERSIONS[from_cat][from_unit.lower()]
            to_factor = UNIT_CONVERSIONS[to_cat][to_unit.lower()]
            result = value * from_factor / to_factor
        
        # Round appropriately
        if result > 100:
            result = round(result, 2)
        elif result > 10:
            result = round(result, 3)
        else:
            result = round(result, 4)
        
        output = f"{value} {from_unit} = **{result} {to_unit}**"
        log.info(f"✅ Converted: {output}")
        print(f"✅ Converter Tool: {output}\n")
        return output
        
    except Exception as e:
        error_msg = f"Cannot convert '{conversion_query}'. Error: {str(e)}"
        log.error(error_msg)
        print(f"❌ Converter Tool: {error_msg}\n")
        return error_msg

# ============================================================================
# GET TOOLS
# ============================================================================

def get_tools():
    """Create and return tool objects."""
    
    wikipedia_tool = SimpleTool(
        name="wikipedia_search",
        description=(
            "Useful for searching Wikipedia and getting information about topics, people, places, "
            "concepts, history, science, etc. Input should be a search query or topic name. "
            "Use this when the user asks 'what is', 'who is', 'tell me about', or wants "
            "information/facts about something."
        ),
        func=wikipedia_search_function
    )
    
    calculator_tool = SimpleTool(
        name="calculator",
        description=(
            "Useful for performing mathematical calculations and arithmetic operations. "
            "Input should be a mathematical expression like '5+3', '144/12', or '2**8'. "
            "Supports +, -, *, /, ** (power), and parentheses. "
            "Use this when the user asks to calculate, compute, or solve a math problem."
        ),
        func=calculator_function
    )
    
    converter_tool = SimpleTool(
        name="unit_converter",
        description=(
            "Useful for converting between different units of measurement. "
            "Input format: 'VALUE UNIT to UNIT' (e.g., '100 kilometers to miles', '5 feet to meters'). "
            "Supports length (km, m, miles, feet, etc), weight (kg, lbs, etc), "
            "temperature (celsius, fahrenheit, kelvin), and volume (liters, gallons, etc). "
            "Use this when the user asks to convert units or asks 'how many X in Y'."
        ),
        func=unit_converter_function
    )
    
    return [wikipedia_tool, calculator_tool, converter_tool]
