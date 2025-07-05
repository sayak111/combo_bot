# DoS Protection Implementation

## What is a DoS Attack?

A **Denial of Service (DoS) attack** is a cyber attack that floods a system with requests to exhaust resources (CPU, memory, network bandwidth) and make the service unavailable to legitimate users.

## DoS Vulnerabilities Identified in Your Bot

### 1. **Message Flooding Attack**
- **Vulnerability**: Users can spam messages in city-selection channels
- **Impact**: Excessive API calls, bot rate limiting, resource exhaustion
- **Solution**: Rate limiting implemented (5 requests per minute per user)

### 2. **Role Assignment Spam**
- **Vulnerability**: Users can rapidly trigger role assignments
- **Impact**: Infinite loops, API rate limit exhaustion
- **Solution**: Rate limiting for role updates (2 updates per 10 seconds per user)

### 3. **Command Abuse**
- **Vulnerability**: Users can spam admin commands
- **Impact**: Bot overload, Discord API rate limiting
- **Solution**: Command rate limiting (3 commands per 30 seconds per user)

### 4. **Logging Spam**
- **Vulnerability**: Users can flood logging channels
- **Impact**: Channel spam, storage issues
- **Solution**: Rate limiting for logging operations

## Implemented Protection Measures

### 1. **Rate Limiting System**
```python
# Configuration in config.py
DOS_PROTECTION = {
    "CITY_SELECTION_RATE_LIMIT_WINDOW": 60,  # seconds
    "MAX_CITY_REQUESTS_PER_WINDOW": 5,  # max requests per user per minute
    
    "COMMAND_RATE_LIMIT_WINDOW": 30,  # seconds
    "MAX_COMMANDS_PER_WINDOW": 3,  # max commands per user per 30 seconds
    
    "ROLE_UPDATE_RATE_LIMIT_WINDOW": 10,  # seconds
    "MAX_ROLE_UPDATES_PER_WINDOW": 2,  # max role updates per user per 10 seconds
}
```

### 2. **User-Friendly Rate Limit Messages**
- Clear feedback when users are rate limited
- Automatic message deletion for rate-limited requests
- Informative messages about limits

### 3. **Memory Management**
- Automatic cleanup of old rate limit data
- Prevention of memory leaks
- Efficient storage of user activity

### 4. **Error Handling**
- Graceful handling of Discord API errors
- Logging of rate limit violations
- Fallback mechanisms for failed operations

## Protection Features

### **City Selection Protection**
- Limits city selection requests to 5 per minute per user
- Prevents spam in city-selection channels
- Automatic cleanup of old requests

### **Command Protection**
- Limits admin commands to 3 per 30 seconds per user
- Prevents command abuse
- Protects against bot overload

### **Role Update Protection**
- Limits role updates to 2 per 10 seconds per user
- Prevents infinite role assignment loops
- Protects Discord API rate limits

### **Combo Role Protection**
- Limits combo role updates to 3 per 30 seconds per user
- Prevents role assignment spam
- Maintains system stability

## Monitoring and Logging

### **Rate Limit Logging**
```python
logging.warning(f"Rate limited {rate_limit_type} for user {user_id}")
```

### **Statistics Tracking**
```python
def get_rate_limit_stats() -> Dict[str, int]:
    """Get statistics about current rate limiting"""
```

### **Memory Cleanup**
```python
def cleanup_old_data(self, max_age_hours: int = 24):
    """Clean up old rate limit data to prevent memory leaks"""
```

## Configuration Options

### **Adjustable Rate Limits**
You can modify rate limits in `config.py`:

```python
DOS_PROTECTION = {
    "CITY_SELECTION_RATE_LIMIT_WINDOW": 60,  # Increase for more lenient limits
    "MAX_CITY_REQUESTS_PER_WINDOW": 5,       # Decrease for stricter limits
    # ... other settings
}
```

### **Different Limits for Different Actions**
- **City Selection**: 5 requests per minute
- **Commands**: 3 commands per 30 seconds
- **Role Updates**: 2 updates per 10 seconds
- **Combo Roles**: 3 updates per 30 seconds

## Best Practices

### **1. Monitor Rate Limit Violations**
- Check logs regularly for rate limit warnings
- Adjust limits based on legitimate usage patterns

### **2. Regular Cleanup**
- Run cleanup operations periodically
- Monitor memory usage

### **3. User Education**
- Inform users about rate limits
- Provide clear feedback when limits are exceeded

### **4. Gradual Adjustments**
- Start with conservative limits
- Adjust based on actual usage patterns
- Monitor for false positives

## Testing DoS Protection

### **Test Rate Limiting**
1. Send multiple rapid messages in city-selection channel
2. Verify rate limit messages appear
3. Check that limits are enforced correctly

### **Test Memory Management**
1. Monitor memory usage during high activity
2. Verify cleanup operations work correctly
3. Check for memory leaks

### **Test Error Handling**
1. Test with Discord API errors
2. Verify graceful degradation
3. Check error logging

## Security Benefits

### **1. API Rate Limit Protection**
- Prevents Discord API rate limiting
- Maintains bot availability
- Reduces API costs

### **2. Resource Protection**
- Prevents CPU/memory exhaustion
- Maintains bot responsiveness
- Protects server resources

### **3. User Experience**
- Prevents spam in channels
- Maintains channel usability
- Provides clear feedback

### **4. System Stability**
- Prevents infinite loops
- Maintains role assignment accuracy
- Protects against cascading failures

## Emergency Procedures

### **If Under Attack**
1. **Immediate Actions**:
   - Temporarily reduce rate limits
   - Monitor logs for attack patterns
   - Consider temporary bot shutdown

2. **Investigation**:
   - Check rate limit statistics
   - Identify attack sources
   - Review recent changes

3. **Recovery**:
   - Block malicious users if necessary
   - Restore normal rate limits
   - Monitor for repeat attacks

### **Rate Limit Bypass Prevention**
- Rate limits are per-user and per-action type
- No global bypass mechanisms
- All actions are rate limited independently

## Conclusion

The implemented DoS protection provides comprehensive defense against:
- Message flooding attacks
- Role assignment spam
- Command abuse
- Logging spam
- Resource exhaustion

The system is configurable, monitorable, and maintains good user experience while protecting against abuse. 