
import csv
import json
import os
import uuid
from datetime import datetime, date
from collections import defaultdict
from decimal import Decimal, InvalidOperation

# ==========================================
# PERSONAL EXPENSE & BUDGET TRACKER
# ==========================================

EXPENSE_FILE = "expenses.csv"
BUDGET_FILE = "budgets.json"

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Education",
    "Entertainment",
    "Bills",
    "Health",
    "Other"
]

FIELDS = ["id", "date", "category", "description", "amount"]


# ==========================================
# 1. FILE HANDLING
# ==========================================

def initialize_files():
    """Create required files if they do not exist."""

    if not os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()

    if not os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "w") as file:
            json.dump({}, file, indent=4)


def load_expenses():
    """Read expense records from CSV."""

    with open(EXPENSE_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_expenses(expenses):
    """Save expense records to CSV."""

    with open(EXPENSE_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(expenses)


def load_budgets():
    """Read monthly budgets from JSON."""

    try:
        with open(BUDGET_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_budgets(budgets):
    """Save monthly budgets to JSON."""

    with open(BUDGET_FILE, "w") as file:
        json.dump(budgets, file, indent=4)


# ==========================================
# 2. INPUT VALIDATION
# ==========================================

def get_valid_amount(message):
    """Accept only positive monetary amounts."""

    while True:
        try:
            amount = Decimal(input(message).strip())

            if not amount.is_finite() or amount <= 0:
                print("Amount must be a positive number.")
                continue

            if amount.as_tuple().exponent < -2:
                print("Maximum two decimal places allowed.")
                continue

            return amount.quantize(Decimal("0.01"))

        except InvalidOperation:
            print("Please enter a valid amount.")


def get_valid_date():
    """Accept a valid date in YYYY-MM-DD format."""

    while True:
        value = input(
            "Enter date (YYYY-MM-DD) or press Enter for today: "
        ).strip()

        if not value:
            return date.today().isoformat()

        try:
            entered_date = datetime.strptime(
                value, "%Y-%m-%d"
            ).date()

            if entered_date > date.today():
                print("Future transaction dates are not allowed.")
                continue

            return entered_date.isoformat()

        except ValueError:
            print("Invalid date. Example: 2026-11-12")


def choose_category():
    """Display and select an expense category."""

    print("\nExpense Categories:")

    for index, category in enumerate(CATEGORIES, 1):
        print(f"{index}. {category}")

    while True:
        try:
            choice = int(input("Select category number: "))

            if 1 <= choice <= len(CATEGORIES):
                return CATEGORIES[choice - 1]

            print("Select a valid category.")

        except ValueError:
            print("Please enter a number.")


# ==========================================
# 3. ADD EXPENSE
# ==========================================

def add_expense():
    print("\n========== ADD EXPENSE ==========")

    expenses = load_expenses()

    transaction_id = str(uuid.uuid4())[:8]
    expense_date = get_valid_date()
    category = choose_category()

    description = input("Enter description: ").strip()

    while not description:
        print("Description cannot be empty.")
        description = input("Enter description: ").strip()

    amount = get_valid_amount("Enter amount (Rs.): ")

    expense = {
        "id": transaction_id,
        "date": expense_date,
        "category": category,
        "description": description,
        "amount": str(amount)
    }

    expenses.append(expense)
    save_expenses(expenses)

    print("\nExpense added successfully!")
    print("Transaction ID:", transaction_id)


# ==========================================
# 4. VIEW EXPENSES
# ==========================================

def view_expenses():
    print("\n========== ALL EXPENSES ==========")

    expenses = load_expenses()

    if not expenses:
        print("No expense records found.")
        return

    expenses.sort(key=lambda x: x["date"], reverse=True)

    print("-" * 90)
    print(f"{'ID':<10} {'DATE':<12} {'CATEGORY':<16} "
          f"{'DESCRIPTION':<25} {'AMOUNT':>12}")
    print("-" * 90)

    for item in expenses:
        print(
            f"{item['id']:<10} "
            f"{item['date']:<12} "
            f"{item['category']:<16} "
            f"{item['description'][:24]:<25} "
            f"{Decimal(item['amount']):>12.2f}"
        )

    print("-" * 90)


# ==========================================
# 5. EDIT EXPENSE
# ==========================================

def edit_expense():
    print("\n========== EDIT EXPENSE ==========")

    expenses = load_expenses()

    transaction_id = input("Enter expense ID: ").strip()

    for item in expenses:

        if item["id"] == transaction_id:

            print("Leave a field empty to keep its current value.")

            new_description = input(
                f"Description ({item['description']}): "
            ).strip()

            if new_description:
                item["description"] = new_description

            new_amount = input(
                f"Amount ({item['amount']}): "
            ).strip()

            if new_amount:
                try:
                    amount = Decimal(new_amount)

                    if not amount.is_finite() or amount <= 0:
                        print("Invalid amount.")
                        return

                    if amount.as_tuple().exponent < -2:
                        print("Maximum two decimal places allowed.")
                        return

                    item["amount"] = str(
                        amount.quantize(Decimal("0.01"))
                    )

                except InvalidOperation:
                    print("Invalid amount.")
                    return

            change_category = input(
                "Change category? (y/n): "
            ).lower().strip()

            if change_category == "y":
                item["category"] = choose_category()

            change_date = input(
                "Change date? (y/n): "
            ).lower().strip()

            if change_date == "y":
                item["date"] = get_valid_date()

            save_expenses(expenses)
            print("Expense updated successfully!")
            return

    print("Expense ID not found.")


# ==========================================
# 6. DELETE EXPENSE
# ==========================================

def delete_expense():
    print("\n========== DELETE EXPENSE ==========")

    expenses = load_expenses()

    transaction_id = input("Enter expense ID: ").strip()

    updated_expenses = [
        item for item in expenses
        if item["id"] != transaction_id
    ]

    if len(updated_expenses) == len(expenses):
        print("Expense not found.")
        return

    confirmation = input(
        "Are you sure you want to delete? (y/n): "
    ).lower().strip()

    if confirmation == "y":
        save_expenses(updated_expenses)
        print("Expense deleted successfully!")
    else:
        print("Deletion cancelled.")


# ==========================================
# 7. SET MONTHLY BUDGET
# ==========================================

def set_budget():
    print("\n========== SET MONTHLY BUDGET ==========")

    current_month = date.today().strftime("%Y-%m")

    month = input(
        f"Enter month (YYYY-MM) [{current_month}]: "
    ).strip()

    if not month:
        month = current_month

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month format.")
        return

    budget_amount = get_valid_amount(
        "Enter monthly budget (Rs.): "
    )

    budgets = load_budgets()
    budgets[month] = str(budget_amount)

    save_budgets(budgets)

    print(f"Budget for {month} saved successfully!")


# ==========================================
# 8. DAILY SPENDING SUMMARY
# ==========================================

def daily_summary():
    print("\n========== DAILY SUMMARY ==========")

    selected_date = get_valid_date()

    expenses = load_expenses()

    daily_expenses = [
        item for item in expenses
        if item["date"] == selected_date
    ]

    if not daily_expenses:
        print("No expenses recorded on this date.")
        return

    total = sum(
        (Decimal(item["amount"]) for item in daily_expenses),
        Decimal("0")
    )

    print("Date:", selected_date)
    print("Number of transactions:", len(daily_expenses))
    print(f"Total spending: Rs. {total:.2f}")


# ==========================================
# 9. MONTHLY SPENDING SUMMARY
# ==========================================

def monthly_summary():
    print("\n========== MONTHLY SUMMARY ==========")

    month = input(
        "Enter month (YYYY-MM): "
    ).strip()

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month format.")
        return

    expenses = load_expenses()

    monthly_expenses = [
        item for item in expenses
        if item["date"].startswith(month)
    ]

    if not monthly_expenses:
        print("No expenses found for this month.")
        return

    total = sum(
        (Decimal(item["amount"]) for item in monthly_expenses),
        Decimal("0")
    )

    print("\nMonth:", month)
    print("Total transactions:", len(monthly_expenses))
    print(f"Total spending: Rs. {total:.2f}")

    budgets = load_budgets()

    if month in budgets:
        budget = Decimal(budgets[month])
        remaining = budget - total

        print(f"Monthly budget: Rs. {budget:.2f}")
        print(f"Remaining budget: Rs. {remaining:.2f}")

        if remaining < 0:
            print("WARNING: Monthly budget exceeded!")
        elif remaining == 0:
            print("You have used your entire budget.")
        else:
            print("You are within your budget.")


# ==========================================
# 10. CATEGORY-WISE SUMMARY
# ==========================================

def category_summary():
    print("\n========== CATEGORY SUMMARY ==========")

    month = input(
        "Enter month (YYYY-MM): "
    ).strip()

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month format.")
        return

    expenses = load_expenses()

    category_totals = defaultdict(Decimal)

    for item in expenses:

        if item["date"].startswith(month):

            category = item["category"]

            category_totals[category] += Decimal(
                item["amount"]
            )

    if not category_totals:
        print("No expense records found.")
        return

    print("\nCategory-wise Spending for", month)

    for category, total in sorted(
        category_totals.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"{category:<20} Rs. {total:.2f}")

    grand_total = sum(
        category_totals.values(),
        Decimal("0")
    )

    print("-" * 40)
    print(f"Total Spending: Rs. {grand_total:.2f}")


# ==========================================
# 11. SEARCH AND FILTER EXPENSES
# ==========================================

def search_expenses():
    print("\n========== SEARCH EXPENSES ==========")

    expenses = load_expenses()

    keyword = input(
        "Enter description keyword: "
    ).strip().lower()

    category = input(
        "Enter category (or press Enter for all): "
    ).strip().lower()

    month = input(
        "Enter month YYYY-MM (or press Enter for all): "
    ).strip()

    if month:
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            print("Invalid month format.")
            return

    results = []

    for item in expenses:

        matches_keyword = (
            keyword in item["description"].lower()
        )

        matches_category = (
            not category or
            category == item["category"].lower()
        )

        matches_month = (
            not month or
            item["date"].startswith(month)
        )

        if (
            matches_keyword
            and matches_category
            and matches_month
        ):
            results.append(item)

    if not results:
        print("No matching expenses found.")
        return

    print("\nSearch Results:")

    for item in results:
        print(
            f"ID: {item['id']} | "
            f"Date: {item['date']} | "
            f"Category: {item['category']} | "
            f"Description: {item['description']} | "
            f"Amount: Rs. {item['amount']}"
        )


# ==========================================
# 12. MAIN MENU
# ==========================================

def main():

    initialize_files()

    while True:

        print("\n")
        print("=" * 48)
        print("       PERSONAL EXPENSE & BUDGET TRACKER")
        print("=" * 48)

        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Set Monthly Budget")
        print("6. Daily Spending Summary")
        print("7. Monthly Spending Summary")
        print("8. Category-wise Summary")
        print("9. Search and Filter Expenses")
        print("0. Exit")

        print("=" * 48)

        choice = input("Enter your choice: ").strip()

        try:

            if choice == "1":
                add_expense()

            elif choice == "2":
                view_expenses()

            elif choice == "3":
                edit_expense()

            elif choice == "4":
                delete_expense()

            elif choice == "5":
                set_budget()

            elif choice == "6":
                daily_summary()

            elif choice == "7":
                monthly_summary()

            elif choice == "8":
                category_summary()

            elif choice == "9":
                search_expenses()

            elif choice == "0":
                print("Thank you for using Expense Tracker!")
                break

            else:
                print("Invalid choice. Please try again.")

        except (OSError, csv.Error, json.JSONDecodeError) as error:
            print("File operation error:", error)

        except (ValueError, InvalidOperation) as error:
            print("Invalid data:", error)


# ==========================================
# PROGRAM EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
