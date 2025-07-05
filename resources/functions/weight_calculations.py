"""
Weight calculation and conversion functions.
Handles weight conversions between units and DOTS score calculations.
"""


CONVERSION_FACTOR_LB_TO_KG = 0.45359237  # multiply lb * this to get kg
CONVERSION_FACTOR_KG_TO_LB = 2.20462262185  # multiply kg * this to get lb
CONVERSION_FACTOR_KG_TO_STONE = 6.35029


def compute_wilks(sex: str, bodyweight_kg: str, total_kg: float) -> str:
    """Compute Wilks score for powerlifting (original formula).
    Inputs must be in kilograms. If pounds are detected, auto-convert to kg."""
    sex_key = "male" if sex.lower().startswith("m") else "female"
    if sex_key == "male":
        a, b, c, d, e = -216.0475144, 16.2606339, -0.002388645, -0.00113732, 7.01863e-06
    else:
        a, b, c, d, e = 594.31747775582, -27.23842536447, 0.82112226871, -0.00930733913, 4.731582e-05
    try:
        bw = float(bodyweight_kg) if bodyweight_kg else 0
        total = float(total_kg) if total_kg else 0
        # If values are suspiciously high, assume pounds and convert to kg
        if bw > 200:  # unlikely to be kg
            bw = bw * CONVERSION_FACTOR_LB_TO_KG
        if total > 500:  # unlikely to be kg
            total = total * CONVERSION_FACTOR_LB_TO_KG
        if bw <= 0 or total <= 0:
            return ""
        wilks_coeff = 500 / (a + b * bw + c * bw ** 2 + d * bw ** 3 + e * bw ** 4)
        wilks = total * wilks_coeff
        return f"{round(wilks + 1e-8, 1)}"
    except (ValueError, TypeError, ZeroDivisionError):
        return ""


def compute_wilks2(sex: str, bodyweight_kg: str, total_kg: float) -> str:
    """Compute Wilks2 score for powerlifting (2020 revised formula).
    Inputs must be in kilograms. If pounds are detected, auto-convert to kg."""
    sex_key = "male" if sex.lower().startswith("m") else "female"
    if sex_key == "male":
        a, b, c, d, e = 47.4617885, 8.47206137, 0.073694103, -0.00139583, 7.07665e-06
    else:
        a, b, c, d, e = -125.425539, 13.7121941, -0.0330725, -0.00105040, 9.38773e-06
    try:
        bw = float(bodyweight_kg) if bodyweight_kg else 0
        total = float(total_kg) if total_kg else 0
        # If values are suspiciously high, assume pounds and convert to kg
        if bw > 200:  # unlikely to be kg
            bw = bw * CONVERSION_FACTOR_LB_TO_KG
        if total > 500:  # unlikely to be kg
            total = total * CONVERSION_FACTOR_LB_TO_KG
        if bw <= 0 or total <= 0:
            return ""
        wilks2_coeff = 600 / (a + b * bw + c * bw ** 2 + d * bw ** 3 + e * bw ** 4)
        wilks2 = total * wilks2_coeff
        return f"{round(wilks2 + 1e-8, 1)}"
    except (ValueError, TypeError, ZeroDivisionError):
        return ""


def compute_ipf(sex: str, bodyweight_kg: str, total_kg: float) -> str:
    """Compute IPF score for powerlifting (IPF formula).
    Inputs must be in kilograms. If pounds are detected, auto-convert to kg."""
    sex_key = "male" if sex.lower().startswith("m") else "female"
    if sex_key == "male":
        a, b, c, d, e = 310.67, 857.785, 53.216, 147.0835, 0
    else:
        a, b, c, d, e = 125.1435, 228.03, 34.5246, 86.8301, 0
    try:
        bw = float(bodyweight_kg) if bodyweight_kg else 0
        total = float(total_kg) if total_kg else 0
        # If values are suspiciously high, assume pounds and convert to kg
        if bw > 200:  # unlikely to be kg
            bw = bw * CONVERSION_FACTOR_LB_TO_KG
        if total > 500:  # unlikely to be kg
            total = total * CONVERSION_FACTOR_LB_TO_KG
        if bw <= 0 or total <= 0:
            return ""
        ipf_coeff = 500 / (a - b * (bw ** (-c)) + d * (bw ** (-2*c)))
        ipf = total * ipf_coeff
        return f"{round(ipf + 1e-8, 1)}"
    except (ValueError, TypeError, ZeroDivisionError):
        return ""


def compute_ipf_gl(sex: str, bodyweight_kg: str, total_kg: float) -> str:
    """Compute IPF GL (Goodlift) score for powerlifting.
    Inputs must be in kilograms. If pounds are detected, auto-convert to kg."""
    sex_key = "male" if sex.lower().startswith("m") else "female"
    if sex_key == "male":
        a, b, c, d, e = 1199.72839, 1025.18162, 0.009210797, 0.0010863365, 1.291E-06
    else:
        a, b, c, d, e = 610.32796, 1045.59282, 0.03048956, 0.0012020432, 1.618E-06
    try:
        bw = float(bodyweight_kg) if bodyweight_kg else 0
        total = float(total_kg) if total_kg else 0
        # If values are suspiciously high, assume pounds and convert to kg
        if bw > 200:  # unlikely to be kg
            bw = bw * CONVERSION_FACTOR_LB_TO_KG
        if total > 500:  # unlikely to be kg
            total = total * CONVERSION_FACTOR_LB_TO_KG
        if bw <= 0 or total <= 0:
            return ""
        ipf_gl_coeff = a - b * (bw ** (-c)) - d * (bw ** 2) - e * (bw ** 3)
        ipf_gl = total / ipf_gl_coeff * 100
        return f"{round(ipf_gl + 1e-8, 1)}"
    except (ValueError, TypeError, ZeroDivisionError):
        return ""

def compute_dots(sex: str, bodyweight_kg: str, total_kg: float) -> str:
    """Compute DOTS score for powerlifting (2020 formula).
    Inputs must be in kilograms. If pounds are detected, auto-convert to kg.
    Returns a string rounded to 1 decimal place, matching the official DOTS calculator."""
    sex_key = "male" if sex.lower().startswith("m") else "female"
    if sex_key == "male":
        a, b, c, d, e = 47.46178854, 8.472061379, 0.07369410346, -0.001395833811, 7.07665973070743e-06
    else:
        a, b, c, d, e = -125.4255398, 13.71219419, -0.03307250631, -0.001050400051, 9.38773881462799e-06
    try:
        bw = float(bodyweight_kg) if bodyweight_kg else 0
        total = float(total_kg) if total_kg else 0
        # If values are suspiciously high, assume pounds and convert to kg
        if bw > 200:  # unlikely to be kg
            bw = bw * CONVERSION_FACTOR_LB_TO_KG
        if total > 500:  # unlikely to be kg
            total = total * CONVERSION_FACTOR_LB_TO_KG
        if bw <= 0 or total <= 0:
            return ""
        dots_coeff = 500.0 / (
            a + b * bw + c * bw ** 2 + d * bw ** 3 + e * bw ** 4
        )
        dots = total * dots_coeff
        # Round to 1 decimal, but ensure correct rounding (match official calculator)
        return f"{round(dots + 1e-8, 1)}"
    except (ValueError, TypeError, ZeroDivisionError):
        return ""


# --- TEST FUNCTION FOR DOTS ---
def _test_dots():
    # Example: Male, 990 lb total, 150 lb bodyweight
    sex = 'male'
    bodyweight_lb = 150
    total_lb = 990
    bodyweight_kg = bodyweight_lb * CONVERSION_FACTOR_LB_TO_KG
    total_kg = total_lb * CONVERSION_FACTOR_LB_TO_KG
    score = compute_dots(sex, bodyweight_lb, total_lb)
    print(f"DOTS (input in lb): {score} (should be ~344.1)")
    score_kg = compute_dots(sex, bodyweight_kg, total_kg)
    print(f"DOTS (input in kg): {score_kg} (should be ~344.1)")


def convert_lb_to_kg(weight_lb: float) -> float:
    """Convert pounds to kilograms."""
    return weight_lb * CONVERSION_FACTOR_LB_TO_KG


def convert_kg_to_lb(weight_kg: float) -> float:
    """Convert kilograms to pounds."""
    return weight_kg * CONVERSION_FACTOR_LB_TO_KG


def convert_kg_to_stone(weight_kg: float) -> float:
    """Convert kilograms to stone."""
    return weight_kg / CONVERSION_FACTOR_KG_TO_STONE


def calculate_total_lifts(user_data: dict) -> float:
    """Calculate total from best lifts for each movement."""
    try:
        # Get best squat
        squat_attempts = [float(user_data.get(f"Squat{i}", 0) or 0) for i in range(1, 4)]
        best_squat = max(squat_attempts) if any(squat_attempts) else 0
        
        # Get best bench
        bench_attempts = [float(user_data.get(f"Bench{i}", 0) or 0) for i in range(1, 4)]
        best_bench = max(bench_attempts) if any(bench_attempts) else 0
        
        # Get best deadlift
        deadlift_attempts = [float(user_data.get(f"Deadlift{i}", 0) or 0) for i in range(1, 4)]
        best_deadlift = max(deadlift_attempts) if any(deadlift_attempts) else 0
        
        return best_squat + best_bench + best_deadlift
    except (ValueError, TypeError):
        return 0.0
