"""
User management functions.
Handles user data loading, saving, validation, and CSV operations.
"""

import os
import csv
import datetime
from typing import List, Dict, Any, Optional
from .utils import resource_path
from .weight_calculations import compute_dots, calculate_total_lifts


# Constants for user data columns
LIFT_COLS = [
    "Bench1", "Bench2", "Bench3",
    "Squat1", "Squat2", "Squat3", 
    "Deadlift1", "Deadlift2", "Deadlift3"
]


def load_users_from_csv() -> List[Dict[str, str]]:
    """Load users from CSV file with default data if file doesn't exist."""
    users = []
    base_path = resource_path("")
    data_dir = os.path.join(base_path, "data")
    csv_path = os.path.join(data_dir, "users.csv")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    if not os.path.exists(csv_path):
        # Create default users
        example_users = create_example_users()
        save_users_to_csv(example_users)
        return example_users
    
    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Ensure all required columns exist
                complete_user = ensure_user_completeness(row)
                users.append(complete_user)
    
    return users


def create_example_users() -> List[Dict[str, str]]:
    """Create example users with default data."""
    example_users = [
        {"First": "Alice", "Last": "Example1", "Age": "28", "Weight_LB": "135", "Weight_KG": "61.2", "Sex": "Female",
         "Bench1": "80", "Bench2": "85", "Bench3": "90",
         "Squat1": "120", "Squat2": "125", "Squat3": "130",
         "Deadlift1": "150", "Deadlift2": "155", "Deadlift3": "160"},
        {"First": "Bob", "Last": "Example2", "Age": "34", "Weight_LB": "185", "Weight_KG": "83.9", "Sex": "Male",
         "Bench1": "110", "Bench2": "115", "Bench3": "120",
         "Squat1": "180", "Squat2": "185", "Squat3": "190",
         "Deadlift1": "210", "Deadlift2": "215", "Deadlift3": "220"},
        {"First": "Carol", "Last": "Example3", "Age": "22", "Weight_LB": "120", "Weight_KG": "54.4", "Sex": "Female",
         "Bench1": "60", "Bench2": "65", "Bench3": "70",
         "Squat1": "100", "Squat2": "105", "Squat3": "110",
         "Deadlift1": "130", "Deadlift2": "135", "Deadlift3": "140"},
        {"First": "David", "Last": "Example4", "Age": "40", "Weight_LB": "200", "Weight_KG": "90.7", "Sex": "Male",
         "Bench1": "120", "Bench2": "125", "Bench3": "130",
         "Squat1": "200", "Squat2": "205", "Squat3": "210",
         "Deadlift1": "230", "Deadlift2": "235", "Deadlift3": "240"},
    ]
    
    # Calculate totals and all scoring systems for each user
    for user in example_users:
        try:
            # Calculate total lifts (in pounds based on user input)
            total_lb = calculate_total_lifts(user)
            user["Total"] = str(total_lb)
            
            # Convert total to kilograms for all calculations
            from .weight_calculations import convert_lb_to_kg, compute_wilks, compute_wilks2, compute_ipf, compute_ipf_gl
            total_kg = convert_lb_to_kg(total_lb)
            
            # Calculate all scoring systems
            sex = user["Sex"]
            weight_kg = user["Weight_KG"]
            
            user["DOTS"] = compute_dots(sex, weight_kg, total_kg)
            user["Wilks"] = compute_wilks(sex, weight_kg, total_kg)
            user["Wilks2"] = compute_wilks2(sex, weight_kg, total_kg)
            user["IPF"] = compute_ipf(sex, weight_kg, total_kg)
            user["IPF_GL"] = compute_ipf_gl(sex, weight_kg, total_kg)
        except Exception:
            user["Total"] = ""
            user["DOTS"] = ""
            user["Wilks"] = ""
            user["Wilks2"] = ""
            user["IPF"] = ""
            user["IPF_GL"] = ""
    
    return example_users


def ensure_user_completeness(user_data: Dict[str, str]) -> Dict[str, str]:
    """Ensure user data has all required columns."""
    required_columns = [
        "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
        *LIFT_COLS,
        "Total", "DOTS", "Wilks", "Wilks2", "IPF", "IPF_GL"
    ]
    
    complete_user = {}
    for col in required_columns:
        complete_user[col] = user_data.get(col, "")
    
    return complete_user


def save_users_to_csv(users: List[Dict[str, str]]) -> bool:
    """Save users list to CSV file."""
    try:
        base_path = resource_path("")
        csv_path = os.path.join(base_path, "data", "users.csv")
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        fieldnames = [
            "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
            *LIFT_COLS,
            "Total", "DOTS"
        ]
        
        with open(csv_path, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user in users:
                writer.writerow({k: user.get(k, "") for k in fieldnames})
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False


def import_users_from_csv_file(filename: str) -> Optional[List[Dict[str, str]]]:
    """Import users from a CSV file."""
    users = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Ensure all columns exist
                complete_user = ensure_user_completeness(row)
                users.append(complete_user)
        return users
    except Exception as e:
        print(f"Failed to import users: {e}")
        return None


def export_users_to_csv_file(users: List[Dict[str, str]], filename: str) -> bool:
    """Export users to a CSV file."""
    try:
        fieldnames = [
            "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
            *LIFT_COLS,
            "Total", "Wilks"
        ]
        
        with open(filename, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user in users:
                writer.writerow({k: user.get(k, "") for k in fieldnames})
        return True
    except Exception as e:
        print(f"Export failed: {e}")
        return False


def save_removed_user(user_data: Dict[str, str]) -> bool:
    """Save a removed user to the removed.csv file."""
    try:
        base_path = resource_path("")
        removed_csv_path = os.path.join(base_path, "data", "removed.csv")
        os.makedirs(os.path.dirname(removed_csv_path), exist_ok=True)
        
        fieldnames = [
            "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
            *LIFT_COLS,
            "Total", "Wilks"
        ]
        
        file_exists = os.path.exists(removed_csv_path)
        with open(removed_csv_path, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({k: user_data.get(k, "") for k in fieldnames})
        return True
    except Exception as e:
        print(f"Error saving to removed.csv: {e}")
        return False


def backup_users_data() -> Optional[str]:
    """Backup current users data with timestamp."""
    try:
        base_path = resource_path("")
        csv_path = os.path.join(base_path, "data", "users.csv")
        today = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        purged_csv_path = os.path.join(base_path, "data", f"users_purged_{today}.csv")
        
        if os.path.exists(csv_path):
            with open(csv_path, "r", encoding="utf-8") as src, open(purged_csv_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        
        return purged_csv_path
    except Exception as e:
        print(f"Backup failed: {e}")
        return None


def update_user_scores(users: List[Dict[str, str]]) -> None:
    """Update all scoring systems (DOTS, Wilks, Wilks2, IPF, IPF GL) for all users."""
    from .weight_calculations import convert_lb_to_kg, compute_wilks, compute_wilks2, compute_ipf, compute_ipf_gl
    
    for user in users:
        try:
            # Calculate total lifts (in pounds based on user input)
            total_lb = calculate_total_lifts(user)
            user["Total"] = str(total_lb)
            
            # Convert total to kilograms for all calculations
            total_kg = convert_lb_to_kg(total_lb)
            
            # Calculate all scoring systems
            sex = user.get("Sex", "")
            weight_kg = user.get("Weight_KG", "")
            
            user["DOTS"] = compute_dots(sex, weight_kg, total_kg)
            user["Wilks"] = compute_wilks(sex, weight_kg, total_kg)
            user["Wilks2"] = compute_wilks2(sex, weight_kg, total_kg)
            user["IPF"] = compute_ipf(sex, weight_kg, total_kg)
            user["IPF_GL"] = compute_ipf_gl(sex, weight_kg, total_kg)
        except Exception:
            user["Total"] = ""
            user["DOTS"] = ""
            user["Wilks"] = ""
            user["Wilks2"] = ""
            user["IPF"] = ""
            user["IPF_GL"] = ""


# Keep the old function name for backward compatibility
def update_user_dots(users: List[Dict[str, str]]) -> None:
    """Update DOTS scores for all users. (Legacy function - use update_user_scores instead)"""
    update_user_scores(users)


def validate_user_data(user_data: Dict[str, str]) -> tuple[bool, str]:
    """Validate user data and return (is_valid, error_message)."""
    if not user_data.get("First", "").strip():
        return False, "First name is required"
    
    if not user_data.get("Last", "").strip():
        return False, "Last name is required"
    
    # Validate numeric fields
    numeric_fields = ["Age", "Weight_LB", "Weight_KG"] + LIFT_COLS
    for field in numeric_fields:
        value = user_data.get(field, "").strip()
        if value:  # Only validate if not empty
            try:
                float(value)
            except ValueError:
                return False, f"{field} must be a valid number"
    
    return True, ""


def filter_users_by_text(users: List[Dict[str, str]], filter_text: str) -> List[Dict[str, str]]:
    """Filter users based on search text."""
    if not filter_text:
        return users
    
    filter_text = filter_text.lower()
    return [
        user for user in users
        if any(filter_text in str(value).lower() for value in user.values())
    ]


def sort_users_by_column(users: List[Dict[str, str]], sort_key: str) -> List[Dict[str, str]]:
    """Sort users by the specified column."""
    numeric_columns = ["Age", "Weight_LB", "Weight_KG"] + LIFT_COLS + ["Total", "DOTS", "Wilks", "Wilks2", "IPF", "IPF_GL"]
    
    if sort_key in numeric_columns:
        try:
            return sorted(users, key=lambda u: float(u.get(sort_key, 0) or 0), reverse=True)
        except Exception:
            return sorted(users, key=lambda u: u.get(sort_key, ""))
    else:
        return sorted(users, key=lambda u: u.get(sort_key, ""))


def load_judge_scores() -> List[Dict[str, str]]:
    """Load judge scores from CSV file."""
    base_path = resource_path("")
    judge_csv = os.path.join(base_path, "data", "judge_scores.csv")
    scores = []
    
    if os.path.exists(judge_csv):
        with open(judge_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                scores.append(row)
    
    return scores
