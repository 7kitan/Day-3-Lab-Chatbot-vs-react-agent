def check_stock(item_name: str) -> str:
    """Returns available quantity and price for a given item."""
    inventory = {
        "iphone": {"quantity": 10, "price": 1000},
        "macbook": {"quantity": 5, "price": 2000},
        "airpods": {"quantity": 0, "price": 200}
    }
    item = item_name.lower().strip()
    if item in inventory:
        data = inventory[item]
        if data["quantity"] > 0:
            return f"{item.capitalize()} is in stock. Quantity: {data['quantity']}, Price: ${data['price']} each."
        else:
            return f"{item.capitalize()} is out of stock."
    return f"Item '{item_name}' not found in inventory."

def get_discount(coupon_code: str) -> str:
    """Returns percentage discount for a valid coupon code. Code must be uppercase."""
    coupons = {
        "WINNER": 10,
        "SAVE20": 20
    }
    if coupon_code in coupons:
        return f"Valid coupon! Discount: {coupons[coupon_code]}%"
    # If it's the right text but wrong case, give a specific hint for failure tracing:
    if coupon_code.upper() in coupons:
        return "Invalid coupon code. Error: Coupon codes are case-sensitive and must be entirely UPPERCASE."
    return f"Coupon '{coupon_code}' is invalid or expired."

def calc_shipping(args_str: str) -> str:
    """Returns the shipping cost based on weight and destination. Arguments: 'weight, destination'"""
    try:
        parts = args_str.split(",")
        if len(parts) < 2:
            return "Error: Missing arguments. Provide both weight and destination separated by a comma (e.g., '1.5, Hanoi')."
        
        weight_kg = float(parts[0].strip())
        destination = parts[1].strip()
        dest = destination.lower()
        
        base_rate = 5.0
        if dest in ["hanoi", "ha noi", "hn"]:
            cost = base_rate + (weight_kg * 2.0)
            return f"Shipping to {destination} for {weight_kg}kg is ${cost}."
        elif dest in ["hcm", "ho chi minh"]:
            cost = base_rate + (weight_kg * 3.0)
            return f"Shipping to {destination} for {weight_kg}kg is ${cost}."
        else:
            cost = base_rate + (weight_kg * 5.0)
            return f"Standard shipping to {destination} for {weight_kg}kg is ${cost}."
    except Exception as e:
        return f"Error executing calc_shipping: {e}. Format MUST be 'weight, destination'"

def get_ecommerce_tools():
    """Returns the list of tool definitions for the ReAct Agent."""
    return [
        {
            "name": "check_stock",
            "description": "Checks the inventory for an item. Argument should be the item name (e.g., 'iphone').",
            "func": check_stock
        },
        {
            "name": "get_discount",
            "description": "Applies a coupon code to get a discount percentage. Argument should be the exact coupon code.",
            "func": get_discount
        },
        {
            "name": "calc_shipping",
            "description": "Calculates shipping cost. Arguments should be provided as 'weight, destination'. Example: '1.5, Hanoi'.",
            "func": calc_shipping
        }
    ]
