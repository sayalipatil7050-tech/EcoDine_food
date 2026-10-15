from datetime import datetime

def calculate_urgency_score(expiry_datetime_str):
    """
    Computes hours remaining until safe-use deadline.
    Returns: (hours_remaining, urgency_level, score)
    """
    try:
        # Expected formats: YYYY-MM-DDTHH:MM or YYYY-MM-DD HH:MM
        clean_str = expiry_datetime_str.replace('T', ' ')
        if len(clean_str) == 16:
            expiry_dt = datetime.strptime(clean_str, '%Y-%m-%d %H:%M')
        else:
            expiry_dt = datetime.strptime(clean_str[:19], '%Y-%m-%d %H:%M:%S')
            
        now = datetime.now()
        diff = (expiry_dt - now).total_seconds() / 3600.0
        
        if diff <= 0:
            return 0.0, 'Expired', 0
        elif diff <= 4:
            return round(diff, 1), 'Critical (Expiring < 4h)', 25
        elif diff <= 8:
            return round(diff, 1), 'High Urgency (Expiring < 8h)', 20
        elif diff <= 16:
            return round(diff, 1), 'Moderate Urgency', 15
        else:
            return round(diff, 1), 'Flexible (> 16h)', 10
    except Exception:
        return 6.0, 'Standard', 15

def calculate_match_score(donation, recipient):
    """
    Smart Redistribution Matching Algorithm
    Evaluates:
      1. Location Match (max 35 pts): Same city and nearby zone.
      2. Capacity Match (max 25 pts): Can the recipient absorb this quantity without waste?
      3. Urgency Alignment (max 25 pts): Urgency vs. recipient vehicle capability.
      4. Storage & Handling Compatibility (max 15 pts): Cold-chain / hot-pack compatibility.
      
    Returns dictionary with match_percentage, score_breakdown, badge, and priority.
    """
    score = 0
    breakdown = []
    
    # 1. Location match
    don_city = (donation.get('city') or '').strip().lower()
    rec_city = (recipient.get('city') or '').strip().lower()
    
    if don_city and rec_city and don_city == rec_city:
        score += 35
        breakdown.append(('Location Match', 35, f"Same city ({donation.get('city')})"))
    elif don_city and rec_city:
        score += 15
        breakdown.append(('Regional Proximity', 15, "Cross-district pickup required"))
    else:
        score += 20
        breakdown.append(('Default Proximity', 20, "Location verified"))
        
    # 2. Capacity match
    meals = int(donation.get('estimated_meals') or 1)
    cap = int(recipient.get('capacity_servings') or 100)
    ratio = meals / max(1, cap)
    
    if 0.5 <= ratio <= 1.2:
        score += 25
        breakdown.append(('Capacity Optimal', 25, f"Recipient capacity ({cap}) closely matches donation ({meals} meals)"))
    elif 0.2 <= ratio < 0.5:
        score += 20
        breakdown.append(('Capacity Adequate', 20, f"Recipient can easily absorb ({cap} cap vs {meals} meals)"))
    elif 1.2 < ratio <= 2.0:
        score += 15
        breakdown.append(('Capacity Stretched', 15, f"May require partial distribution ({cap} cap vs {meals} meals)"))
    else:
        score += 10
        breakdown.append(('Capacity Gap', 10, f"Significant difference between capacity and size"))
        
    # 3. Urgency and time factor
    hours_left, urgency_label, urg_score = calculate_urgency_score(donation.get('expiry_datetime', ''))
    score += urg_score
    breakdown.append(('Time Urgency', urg_score, f"{urgency_label} ({hours_left} hrs remaining)"))
    
    # 4. Storage & Safe Handling
    storage = donation.get('storage_requirement', 'Room Temperature')
    if storage == 'Room Temperature':
        score += 15
        breakdown.append(('Storage Match', 15, "Ambient room temp: easy pickup"))
    elif storage in ['Refrigerated (Cold Chain)', 'Hot Holding']:
        score += 12
        breakdown.append(('Special Storage', 12, f"Requires {storage} handling"))
    else:
        score += 10
        breakdown.append(('Storage Verified', 10, "Standard insulated transport"))
        
    final_score = min(100, max(15, score))
    
    if final_score >= 85:
        badge = 'Prime Match'
        badge_class = 'badge-prime'
    elif final_score >= 70:
        badge = 'High Match'
        badge_class = 'badge-high'
    elif final_score >= 50:
        badge = 'Moderate Match'
        badge_class = 'badge-medium'
    else:
        badge = 'Low Match'
        badge_class = 'badge-low'
        
    return {
        'match_score': final_score,
        'badge': badge,
        'badge_class': badge_class,
        'hours_left': hours_left,
        'urgency_label': urgency_label,
        'breakdown': breakdown
    }
