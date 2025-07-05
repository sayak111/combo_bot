# DoS Protection System

This Discord bot includes comprehensive protection against various types of denial of service attacks and spam.

## 🛡️ Protection Features

### 1. Rate Limiting
- **Command Rate Limiting**: Limits how often users can use commands
- **City Selection Rate Limiting**: Prevents spam in city selection channels
- **Role Update Rate Limiting**: Protects against rapid role changes
- **Combo Role Rate Limiting**: Prevents abuse of combo role system

### 2. Spam Detection
- **Repeated Message Detection**: Detects when users send identical messages repeatedly
- **Message Flood Protection**: Limits total messages per user per minute
- **Content Analysis**: Tracks message patterns to identify spam

### 3. Memory Management
- **Automatic Cleanup**: Removes old rate limit data to prevent memory leaks
- **Configurable Retention**: Adjustable data retention periods
- **Statistics Tracking**: Monitor protection effectiveness

## ⚙️ Configuration

All protection settings are configurable in `config.py`:

```python
DOS_PROTECTION = {
    # Rate limiting windows (in seconds)
    "CITY_SELECTION_RATE_LIMIT_WINDOW": 60,
    "COMMAND_RATE_LIMIT_WINDOW": 30,
    "ROLE_UPDATE_RATE_LIMIT_WINDOW": 10,
    "COMBO_ROLE_UPDATE_RATE_LIMIT_WINDOW": 30,
    
    # Maximum requests per window
    "MAX_CITY_SELECTION_PER_WINDOW": 5,
    "MAX_COMMANDS_PER_WINDOW": 3,
    "MAX_ROLE_UPDATES_PER_WINDOW": 2,
    "MAX_COMBO_ROLE_UPDATES_PER_WINDOW": 3,
    
    # Spam detection
    "SPAM_WINDOW": 60,
    "MAX_REPEATED_MESSAGES": 3,
    "MAX_MESSAGES_PER_MINUTE": 10,
    
    # Command cooldowns
    "COMMAND_COOLDOWNS": {
        "city_selection": 5,
        "role_updates": 10,
        "admin_commands": 30,
    }
}
```

## 🔧 Admin Commands

### `!dosstats`
Shows current DoS protection statistics including:
- Number of rate-limited users by type
- Spam detection statistics
- Active protection data

### `!cleanup`
Manually triggers cleanup of old protection data to free memory.

### `!dosconfig`
Displays current DoS protection configuration settings.

### `!status`
Shows overall bot status including:
- Guild and user counts
- Bot latency
- Cog status

## 🚨 Protection Responses

When protection is triggered, the bot will:

1. **Log the incident** with user ID and details
2. **Send a warning message** to the user (auto-deleted after 10 seconds)
3. **Delete the triggering message** if possible
4. **Continue normal operation** for other users

### Example Responses:
- Rate limiting: `⏰ @user Please wait before making another request. Rate limit: 3 requests per 30 seconds.`
- Spam detection: `🚫 @user Please slow down your messages to avoid spam detection.`

## 📊 Monitoring

### Log Messages
The system logs all protection events:
```
WARNING: Rate limited commands for user 123456789
WARNING: Spam detected for user 123456789: repeated message 'hello...'
```

### Statistics Tracking
- Track how many users are currently rate-limited
- Monitor spam detection effectiveness
- Monitor memory usage of protection data

## 🛠️ Implementation Details

### Rate Limiting Algorithm
1. **Sliding Window**: Uses timestamps to track requests within configurable windows
2. **Automatic Cleanup**: Removes expired timestamps to prevent memory bloat
3. **Per-User Tracking**: Each user has independent rate limit counters

### Spam Detection Algorithm
1. **Content Tracking**: Stores recent messages with timestamps
2. **Repetition Detection**: Counts identical messages within time window
3. **Flood Detection**: Limits total messages per user per minute
4. **Automatic Cleanup**: Removes old message data

### Memory Management
1. **24-Hour Retention**: Protection data is automatically cleaned up after 24 hours
2. **Configurable Cleanup**: Admin can trigger manual cleanup
3. **Statistics Monitoring**: Track memory usage and active users

## 🔒 Security Best Practices

1. **Logging**: All protection events are logged for monitoring
2. **Graceful Handling**: Bot continues operating even if protection fails
3. **Permission Checks**: Admin commands require proper permissions
4. **Error Handling**: Comprehensive error handling prevents crashes
5. **Configurable Limits**: Easy to adjust protection levels as needed

## 🚀 Usage Examples

### Adjusting Protection Levels
```python
# Make protection more strict
DOS_PROTECTION["MAX_COMMANDS_PER_WINDOW"] = 2
DOS_PROTECTION["COMMAND_RATE_LIMIT_WINDOW"] = 60

# Make protection more lenient
DOS_PROTECTION["MAX_COMMANDS_PER_WINDOW"] = 5
DOS_PROTECTION["COMMAND_RATE_LIMIT_WINDOW"] = 15
```

### Monitoring Protection
```bash
# Check protection statistics
!dosstats

# Clean up old data
!cleanup

# View current configuration
!dosconfig
```

## 🎯 Protection Targets

This system protects against:

1. **Command Spam**: Rapid command execution
2. **Message Flooding**: Too many messages in short time
3. **Role Abuse**: Rapid role changes
4. **City Selection Spam**: Repeated city selection attempts
5. **Combo Role Exploitation**: Abusing combo role logic
6. **Memory Exhaustion**: Prevents memory leaks from protection data

## 📈 Performance Impact

- **Minimal Overhead**: Protection checks are fast and efficient
- **Memory Efficient**: Automatic cleanup prevents memory bloat
- **Scalable**: Works with any number of users
- **Configurable**: Can be tuned for different server sizes

The protection system is designed to be transparent to normal users while effectively preventing abuse and spam. 