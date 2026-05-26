import frappe
from frappe import _
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two coordinates using Haversine formula"""
    R = 6371000  # Earth radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def get_customer_location(customer):
    """Get saved location for customer"""
    loc = frappe.db.get_value("SFA Saved Location", 
        {"linked_customer": customer, "location_type": "Customer", "is_active": 1},
        ["latitude", "longitude", "accuracy"], as_dict=True)
    return loc

def is_within_geofence(lat, lon, center_lat, center_lon, radius_meters):
    """Check if coordinate is within geofence"""
    distance = calculate_distance(lat, lon, center_lat, center_lon)
    return distance <= radius_meters
