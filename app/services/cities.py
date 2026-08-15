"""Curated database of Pakistani + South Asian cities with coordinates.

lat/lng are decimal degrees (WGS84). timezone is an IANA zone name.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class City:
    id: int
    name: str
    country: str
    lat: float
    lng: float
    timezone: str
    population: int | None = None


CITIES: list[City] = [
    # ---- Pakistan ----
    City(1, "Karachi", "Pakistan", 24.8607, 67.0011, "Asia/Karachi", 17236000),
    City(2, "Lahore", "Pakistan", 31.5204, 74.3587, "Asia/Karachi", 13022000),
    City(3, "Faisalabad", "Pakistan", 31.4504, 73.1350, "Asia/Karachi", 3322000),
    City(4, "Rawalpindi", "Pakistan", 33.5651, 73.0169, "Asia/Karachi", 2098000),
    City(5, "Islamabad", "Pakistan", 33.6844, 73.0479, "Asia/Karachi", 1098000),
    City(6, "Multan", "Pakistan", 30.1575, 71.5249, "Asia/Karachi", 1872000),
    City(7, "Peshawar", "Pakistan", 34.0151, 71.5249, "Asia/Karachi", 1970000),
    City(8, "Quetta", "Pakistan", 30.1798, 66.9750, "Asia/Karachi", 1001000),
    City(9, "Hyderabad", "Pakistan", 25.3960, 68.3578, "Asia/Karachi", 1732000),
    City(10, "Sialkot", "Pakistan", 32.4945, 74.5229, "Asia/Karachi", 655000),
    City(11, "Gujranwala", "Pakistan", 32.1877, 74.1945, "Asia/Karachi", 2027000),
    City(12, "Sargodha", "Pakistan", 32.0836, 72.6711, "Asia/Karachi", 659000),
    City(13, "Bahawalpur", "Pakistan", 29.3956, 71.6836, "Asia/Karachi", 762000),
    City(14, "Sukkur", "Pakistan", 27.7052, 68.8574, "Asia/Karachi", 499000),
    City(15, "Larkana", "Pakistan", 27.5490, 68.2172, "Asia/Karachi", 490000),
    City(16, "Sheikhupura", "Pakistan", 31.7167, 73.9850, "Asia/Karachi", 474000),
    City(17, "Mirpur Khas", "Pakistan", 25.5291, 69.0112, "Asia/Karachi", 440000),
    City(18, "Mardan", "Pakistan", 34.1989, 72.0231, "Asia/Karachi", 358000),
    City(19, "Gujrat", "Pakistan", 32.5742, 74.0754, "Asia/Karachi", 390000),
    City(20, "Abbottabad", "Pakistan", 34.1688, 73.2215, "Asia/Karachi", 200000),
    City(21, "Jhelum", "Pakistan", 32.9345, 73.7310, "Asia/Karachi", 190000),
    City(22, "Sahiwal", "Pakistan", 30.6682, 73.1115, "Asia/Karachi", 390000),
    City(23, "Okara", "Pakistan", 30.8105, 73.4515, "Asia/Karachi", 310000),
    City(24, "Gwadar", "Pakistan", 25.1218, 62.3254, "Asia/Karachi", 90000),
    City(25, "Khairpur", "Pakistan", 27.5295, 68.7590, "Asia/Karachi", 190000),
    City(26, "Nawabshah", "Pakistan", 26.2442, 68.4100, "Asia/Karachi", 280000),
    City(27, "Chiniot", "Pakistan", 31.7200, 72.9784, "Asia/Karachi", 227000),
    City(28, "Kasur", "Pakistan", 31.1156, 74.4469, "Asia/Karachi", 314000),
    City(29, "Muzaffarabad", "Pakistan", 34.3700, 73.4714, "Asia/Karachi", 149000),
    City(30, "Gilgit", "Pakistan", 35.9186, 74.3125, "Asia/Karachi", 99000),
    City(31, "Skardu", "Pakistan", 35.2971, 75.6261, "Asia/Karachi", 52000),
    City(32, "Chitral", "Pakistan", 35.8519, 71.7864, "Asia/Karachi", 42000),
    City(33, "Swat (Mingora)", "Pakistan", 34.7719, 72.3601, "Asia/Karachi", 279000),
    City(34, "Kohat", "Pakistan", 33.5869, 71.4414, "Asia/Karachi", 228000),
    City(35, "Bannu", "Pakistan", 32.9889, 70.6056, "Asia/Karachi", 105000),
    City(36, "Dera Ghazi Khan", "Pakistan", 30.0506, 70.6347, "Asia/Karachi", 464000),
    City(37, "Rahim Yar Khan", "Pakistan", 28.4202, 70.2952, "Asia/Karachi", 420000),
    City(38, "Vehari", "Pakistan", 30.0451, 72.3488, "Asia/Karachi", 155000),
    City(39, "Murree", "Pakistan", 33.9067, 73.3903, "Asia/Karachi", 25000),
    # ---- South Asia ----
    City(100, "Delhi", "India", 28.6139, 77.2090, "Asia/Kolkata", 32941000),
    City(101, "Mumbai", "India", 19.0760, 72.8777, "Asia/Kolkata", 20667000),
    City(102, "Dhaka", "Bangladesh", 23.8103, 90.4125, "Asia/Dhaka", 22178000),
    City(103, "Chittagong", "Bangladesh", 22.3569, 91.7832, "Asia/Dhaka", 5405000),
    City(104, "Kolkata", "India", 22.5726, 88.3639, "Asia/Kolkata", 14974000),
    City(105, "Colombo", "Sri Lanka", 6.9271, 79.8612, "Asia/Colombo", 752993),
    City(106, "Kabul", "Afghanistan", 34.5553, 69.2075, "Asia/Kabul", 4630000),
    City(107, "Kathmandu", "Nepal", 27.7172, 85.3240, "Asia/Kathmandu", 975453),
    City(108, "Male", "Maldives", 4.1755, 73.5093, "Indian/Maldives", 252768),
    City(109, "Dubai", "UAE", 25.2048, 55.2708, "Asia/Dubai", 3600000),
    City(110, "Riyadh", "Saudi Arabia", 24.7136, 46.6753, "Asia/Riyadh", 7677000),
    City(111, "Makkah", "Saudi Arabia", 21.4225, 39.8262, "Asia/Riyadh", 2000000),
    City(112, "Madinah", "Saudi Arabia", 24.5247, 39.5692, "Asia/Riyadh", 1483000),
    City(113, "Jeddah", "Saudi Arabia", 21.4858, 39.1925, "Asia/Riyadh", 4300000),
    City(114, "Kuala Lumpur", "Malaysia", 3.1390, 101.6869, "Asia/Kuala_Lumpur", 1960000),
    City(115, "Singapore", "Singapore", 1.3521, 103.8198, "Asia/Singapore", 5900000),
    City(116, "London", "United Kingdom", 51.5074, -0.1278, "Europe/London", 8982000),
    City(117, "New York", "United States", 40.7128, -74.0060, "America/New_York", 8419000),
    City(118, "Toronto", "Canada", 43.6532, -79.3832, "America/Toronto", 2930000),
    City(119, "Sydney", "Australia", -33.8688, 151.2093, "Australia/Sydney", 5312000),
    City(120, "Istanbul", "Türkiye", 41.0082, 28.9784, "Europe/Istanbul", 15460000),
    City(121, "Doha", "Qatar", 25.2854, 51.5310, "Asia/Qatar", 2330000),
    City(122, "Kuwait City", "Kuwait", 29.3759, 47.9774, "Asia/Kuwait", 3000000),
    City(123, "Muscat", "Oman", 23.5880, 58.3829, "Asia/Muscat", 1600000),
]


# Search helper
def search_cities(query: str, limit: int = 8) -> list[City]:
    q = query.strip().lower()
    if not q:
        return CITIES[:limit]
    results = [c for c in CITIES if q in c.name.lower() or q in c.country.lower()]
    return results[:limit]
