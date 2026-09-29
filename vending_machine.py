# ─────────────────────────────────────────────
#  Vending Machine — Philippine Peso (Python)
# ─────────────────────────────────────────────

inventory = {
    "A1": {"name": "Cola",         "price": 35,  "qty": 5},
    "A2": {"name": "Water",        "price": 20,  "qty": 8},
    "A3": {"name": "Orange Juice", "price": 45,  "qty": 3},
    "B1": {"name": "Chips",        "price": 30,  "qty": 6},
    "B2": {"name": "Chocolate",    "price": 40,  "qty": 4},
    "B3": {"name": "Granola Bar",  "price": 55,  "qty": 2},
    "C1": {"name": "Gum",          "price": 15,  "qty": 10},
    "C2": {"name": "Mints",        "price": 10,  "qty": 0},
    "C3": {"name": "Cookies",      "price": 35,  "qty": 3},
}

DENOMINATIONS = [1000, 500, 200, 100, 50, 20, 10, 5, 1]


def fmt(amount):
    return f"₱{amount:.2f}"


def display_inventory():
    print("\n" + "=" * 50)
    print(f"  {'CODE':<6} {'ITEM':<18} {'PRICE':>8}  {'STOCK':>5}")
    print("=" * 50)
    for code, item in inventory.items():
        stock = item["qty"] if item["qty"] > 0 else "OUT"
        print(f"  {code:<6} {item['name']:<18} {fmt(item['price']):>8}  {str(stock):>5}")
    print("=" * 50)


def display_cart(cart):
    if not cart:
        print("\n  Cart is empty.")
        return
    print("\n" + "-" * 50)
    print(f"  {'CODE':<6} {'ITEM':<18} {'QTY':>4}  {'SUBTOTAL':>10}")
    print("-" * 50)
    total = 0
    for code, qty in cart.items():
        item = inventory[code]
        subtotal = item["price"] * qty
        total += subtotal
        print(f"  {code:<6} {item['name']:<18} {qty:>4}  {fmt(subtotal):>10}")
    print("-" * 50)
    print(f"  {'TOTAL':<28} {fmt(total):>10}")
    print("-" * 50)
    return total


def add_to_cart(cart):
    while True:
        code = input("\n  Enter item code (or 'done' to stop): ").strip().upper()
        if code == "DONE":
            break

        if code not in inventory:
            print(f"  [ERROR] Invalid code '{code}'. Please try again.")
            continue

        item = inventory[code]

        if item["qty"] == 0:
            print(f"  [ERROR] '{item['name']}' is out of stock.")
            continue

        in_cart = cart.get(code, 0)
        available = item["qty"] - in_cart

        if available <= 0:
            print(f"  [ERROR] No more '{item['name']}' available (already {in_cart} in cart).")
            continue

        try:
            qty_str = input(f"  How many '{item['name']}' ({fmt(item['price'])} each)? [max {available}]: ").strip()
            qty = int(qty_str)
        except ValueError:
            print("  [ERROR] Please enter a valid number.")
            continue

        if qty <= 0:
            print("  [ERROR] Quantity must be at least 1.")
            continue

        if qty > available:
            print(f"  [ERROR] Only {available} available.")
            continue

        cart[code] = in_cart + qty
        print(f"  [OK] Added {qty}x {item['name']} to cart.")


def insert_payment(total):
    print(f"\n  Amount due: {fmt(total)}")
    print(f"  Accepted denominations: ₱1, ₱5, ₱10, ₱20, ₱50, ₱100, ₱200, ₱500, ₱1000")
    balance = 0

    while balance < total:
        remaining = total - balance
        print(f"  Balance inserted: {fmt(balance)}  |  Still needed: {fmt(remaining)}")
        try:
            amount = float(input("  Insert coin/bill: ₱").strip())
        except ValueError:
            print("  [ERROR] Invalid amount. Please enter a number.")
            continue

        if amount not in DENOMINATIONS:
            print(f"  [ERROR] ₱{amount:.0f} is not an accepted denomination.")
            continue

        balance += amount
        print(f"  [OK] Inserted {fmt(amount)}. Total inserted: {fmt(balance)}")

    return balance


def give_change(change):
    if change == 0:
        print("\n  Exact payment. No change.")
        return

    print(f"\n  Change to return: {fmt(change)}")
    remaining = int(round(change))
    breakdown = []

    for denom in DENOMINATIONS:
        count = remaining // denom
        if count > 0:
            breakdown.append(f"{count}x ₱{denom}")
            remaining -= count * denom

    print(f"  Bills/coins: {', '.join(breakdown)}")


def dispense(cart):
    print("\n  Dispensing items...")
    for code, qty in cart.items():
        item = inventory[code]
        inventory[code]["qty"] -= qty
        print(f"  [DISPENSED] {item['name']} x{qty}")


def run():
    print("\n" + "=" * 50)
    print("       WELCOME TO THE VENDING MACHINE")
    print("             Philippine Peso (₱)")
    print("=" * 50)

    while True:
        display_inventory()

        print("\n  OPTIONS:")
        print("  [1] Start shopping")
        print("  [2] Exit")
        choice = input("\n  Choose an option: ").strip()

        if choice == "2":
            print("\n  Thank you for using the vending machine! Goodbye.\n")
            break

        if choice != "1":
            print("  [ERROR] Invalid option.")
            continue

        cart = {}

        # Add items to cart
        add_to_cart(cart)

        if not cart:
            print("\n  No items selected. Returning to menu.")
            continue

        # Show cart summary
        print("\n  --- CART SUMMARY ---")
        total = display_cart(cart)

        confirm = input("\n  Proceed to payment? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("  Transaction cancelled.")
            continue

        # Payment
        balance = insert_payment(total)
        change = balance - total

        # Dispense and give change
        dispense(cart)
        give_change(change)

        print("\n  ✓ Transaction complete! Enjoy your items.")

        again = input("\n  Make another purchase? (yes/no): ").strip().lower()
        if again != "yes":
            print("\n  Thank you! Goodbye.\n")
            break


if __name__ == "__main__":
    run()
