# Combo Bot

A Discord bot for managing combo roles and city selection functionality with comprehensive DoS protection.

## Features

- **Combo Role Management**: Automatically assigns combo roles when users have both leader and location roles
- **City Selection**: Handles city role assignment in designated channels
- **DoS Protection**: Comprehensive rate limiting to prevent abuse
- **Admin Commands**: Server management utilities for administrators

## Project Structure

```
combo_bot/
├── bot.py                  # Main entry point
├── config.py               # Configuration and constants
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── cogs/                  # Bot features as modular cogs
│   ├── __init__.py
│   ├── combo_roles.py     # Combo role logic
│   ├── city_pick.py       # City selection logic
│   └── admin.py           # Admin commands
│
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── dos_protection.py  # Rate limiting logic
│   └── logging_config.py  # Logging setup
│
└── data/                  # Data files
    └── secrets.toml       # Bot token and secrets
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Secrets**:
   Create `data/secrets.toml` with your Discord bot token:
   ```toml
   [discord]
   token = "your-bot-token-here"
   ```

3. **Configure Roles**:
   Update `config.py` with your server's roles and settings.

4. **Run the Bot**:
   ```bash
   python bot.py
   ```

## Configuration

### Role Configuration

Edit `config.py` to match your server's roles:

```python
# Country roles
COUNTRY_ROLES = {"Israel", "USA", "Canada", "Germany", "Other"}

# City roles mapping
CITY_ROLES = {
    "netanya": "IL Netanya",
    "modiin": "IL Modi'in",
    "rehovot": "IL Rehovot",
    # Add more cities here
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
```

### DoS Protection

The bot includes comprehensive rate limiting:

- **Commands**: 3 commands per 30 seconds
- **City Selection**: 5 requests per minute
- **Role Updates**: 2 updates per 10 seconds
- **Combo Role Updates**: 3 updates per 30 seconds

## Commands

### Admin Commands (Admin only)

- `!reset_combo_roles` - Reset combo roles for all members
- `!listroles` - List all roles in the server
- `!getchannels` - List all channels in the server
- `!sge_help` - Show admin command help

### City Selection

In channels with "city-selection" in the name:
- Type a city name (e.g., `netanya`, `modiin`) to get the corresponding role
- Type `other` for instructions on adding new cities
- Type `other your-city-name` to submit a new city for review

## Features

### Combo Role System

The bot automatically assigns combo roles when users have both:
1. A leader role (Director, Co-Director, etc.)
2. A location role (Netanya, Modi'in, etc.)

Combo roles follow the format: `{Location} Leader`

### City Role Management

- Users can select their city in designated channels
- Existing city roles are automatically removed when selecting a new one
- Unrecognized cities are logged for review

### DoS Protection

- Rate limiting prevents spam and abuse
- Automatic cleanup of old rate limit data
- Configurable limits for different actions

## Development

### Adding New Features

1. Create a new cog in the `cogs/` directory
2. Follow the cog pattern with `setup(bot)` function
3. Add the cog to `bot.py`

### Logging

The bot uses structured logging with different levels:
- `INFO`: General bot activity
- `WARNING`: Issues that don't stop operation
- `ERROR`: Serious issues

## Troubleshooting

### Common Issues

1. **Bot can't assign roles**: Check bot permissions in Discord
2. **Rate limiting too strict**: Adjust limits in `config.py`
3. **Cogs not loading**: Check for syntax errors in cog files

### Logs

Check the console output for detailed logs. The bot logs all important events and errors.

## License

This project is for internal use only. 