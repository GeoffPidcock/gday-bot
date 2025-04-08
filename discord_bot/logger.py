"""
Logging module for G'Day Bot interactions
"""
import os
import json
import datetime
import threading
from typing import Dict, List, Any, Optional

# Constants
LOG_DIR = os.environ.get("LOG_DIR", "./logs")
INTERACTIONS_LOG = os.path.join(LOG_DIR, "interactions.json")
ERRORS_LOG = os.path.join(LOG_DIR, "errors.json")
REACTIONS_LOG = os.path.join(LOG_DIR, "reactions.json")

# Thread lock for file access
file_lock = threading.Lock()

def _ensure_log_dir_exists():
    """Ensure the logs directory exists"""
    os.makedirs(LOG_DIR, exist_ok=True)

def _load_log_file(log_file: str) -> List[Dict[str, Any]]:
    """Load a log file or create it if it doesn't exist"""
    _ensure_log_dir_exists()
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        print(f"Error loading log file {log_file}: {str(e)}")
        return []

def _append_to_log(log_file: str, entry: Dict[str, Any]):
    """Append an entry to a log file with thread safety"""
    with file_lock:
        logs = _load_log_file(log_file)
        logs.append(entry)
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing to log file {log_file}: {str(e)}")

def log_interaction(
    query: str,
    response: str,
    user_id: str,
    username: str,
    guild_id: str = "unknown",
    channel_id: str = "unknown",
    message_id: str = "unknown",
    matches: Optional[List[Dict[str, Any]]] = None
):
    """
    Log an interaction with the bot
    
    Args:
        query: The user's query
        response: The bot's response
        user_id: Discord user ID
        username: Discord username
        guild_id: Discord server ID (or "DM" for direct messages)
        channel_id: Discord channel ID
        message_id: Discord message ID
        matches: List of matches from the RAG system
    """
    timestamp = datetime.datetime.now().isoformat()
    
    entry = {
        "timestamp": timestamp,
        "message_id": message_id,
        "user_id": user_id,
        "username": username,
        "guild_id": guild_id,
        "channel_id": channel_id,
        "query": query,
        "response": response,
        "matches": matches if matches else []
    }
    
    _append_to_log(INTERACTIONS_LOG, entry)

def log_reaction(
    message_id: str,
    user_id: str,
    username: str,
    emoji: str,
    is_positive: bool = None
):
    """
    Log a reaction to a bot message
    
    Args:
        message_id: Discord message ID
        user_id: Discord user ID
        username: Discord username
        emoji: The reaction emoji
        is_positive: Whether the reaction is positive (👍, ❤️) 
    """
    timestamp = datetime.datetime.now().isoformat()
    
    entry = {
        "timestamp": timestamp,
        "message_id": message_id,
        "user_id": user_id,
        "username": username,
        "emoji": emoji,
        "is_positive": is_positive
    }
    
    _append_to_log(REACTIONS_LOG, entry)

def log_error(
    error_type: str,
    details: str,
    user_id: str = "unknown",
    message_id: str = "unknown"
):
    """
    Log an error
    
    Args:
        error_type: Type of error
        details: Error details
        user_id: Discord user ID
        message_id: Discord message ID
    """
    timestamp = datetime.datetime.now().isoformat()
    
    entry = {
        "timestamp": timestamp,
        "error_type": error_type,
        "details": details,
        "user_id": user_id,
        "message_id": message_id
    }
    
    _append_to_log(ERRORS_LOG, entry)

def get_recent_interactions(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the most recent interactions
    
    Args:
        limit: Maximum number of interactions to return
        
    Returns:
        List of recent interactions
    """
    logs = _load_log_file(INTERACTIONS_LOG)
    
    # Sort by timestamp (newest first)
    sorted_logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Return the most recent entries
    return sorted_logs[:limit]

def get_interaction_stats() -> Dict[str, Any]:
    """
    Get interaction statistics
    
    Returns:
        Dictionary with statistics
    """
    interactions = _load_log_file(INTERACTIONS_LOG)
    reactions = _load_log_file(REACTIONS_LOG)
    errors = _load_log_file(ERRORS_LOG)
    
    # Count positive reactions
    positive_reactions = sum(1 for r in reactions if r.get("is_positive", False))
    
    # Get unique users
    unique_users = set(i.get("user_id") for i in interactions)
    
    return {
        "total_interactions": len(interactions),
        "total_reactions": len(reactions),
        "positive_reactions": positive_reactions,
        "total_errors": len(errors),
        "unique_users": len(unique_users)
    }