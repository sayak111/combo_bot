# config.py

# Log file for unrecognized cities
LOG_FILE = "unrecognized_cities.txt"
UNRECOGNIZED_CITY_CHANNEL = "unrecognized-cities"
UNRECOGNIZED_CITY_CATEGORY = "City selection"

# DoS Protection Configuration
DOS_PROTECTION = {
    # City selection rate limiting
    "CITY_SELECTION_RATE_LIMIT_WINDOW": 60,  # seconds
    "MAX_CITY_REQUESTS_PER_WINDOW": 5,  # max requests per user per minute
    
    # Command rate limiting
    "COMMAND_RATE_LIMIT_WINDOW": 30,  # seconds
    "MAX_COMMANDS_PER_WINDOW": 3,  # max commands per user per 30 seconds
    
    # Role update rate limiting
    "ROLE_UPDATE_RATE_LIMIT_WINDOW": 10,  # seconds
    "MAX_ROLE_UPDATES_PER_WINDOW": 2,  # max role updates per user per 10 seconds
    
    # Combo role update rate limiting
    "COMBO_ROLE_RATE_LIMIT_WINDOW": 30,  # seconds
    "MAX_COMBO_ROLE_UPDATES_PER_WINDOW": 3,  # max updates per user per 30 seconds
    
    # Message flood protection
    "MAX_MESSAGES_PER_MINUTE": 10,  # max messages per user per minute
    "FLOOD_WINDOW": 60,  # seconds
}

COUNTRY_ROLES = {"Israel", "USA", "Canada", "Germany", "Other"}

# City role logic
CITY_ROLES = {
    "netanya": "IL Netanya",
    "modiin": "IL Modi'in",
    "rehovot": "IL Rehovot",
    # Add more here
}

# Leader roles
LEADER_ROLES = {
    "Director",
    "Co-Director",
    "Ambassador",
    "Operations/Media Volunteer"
}

# Locations
LOCATIONS = {
    "Netanya",
    "Modi'in",
    "Rehovot"
} 