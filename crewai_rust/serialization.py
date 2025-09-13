"""
High-performance serialization engine using Rust backend.

This module provides a drop-in replacement for CrewAI's serialization
systems with zero-copy optimizations and performance improvements.
"""

import os
import json
from typing import Any, Dict, Optional
from . import HAS_RUST_IMPLEMENTATION

# Try to import the Rust implementation
if HAS_RUST_IMPLEMENTATION:
    try:
        from ._core import AgentMessage as _AgentMessage
        _RUST_AVAILABLE = True
    except ImportError:
        _RUST_AVAILABLE = False
else:
    _RUST_AVAILABLE = False


class AgentMessage:
    """
    High-performance message serialization using Rust backend.
    
    This class provides a drop-in replacement for CrewAI's message serialization
    with zero-copy optimizations and performance improvements while maintaining full
    API compatibility.
    """
    
    def __init__(
        self, 
        id: str, 
        sender: str, 
        recipient: str, 
        content: str, 
        timestamp: int,
        use_rust: Optional[bool] = None
    ):
        """
        Initialize an agent message.
        
        Args:
            id: Message ID
            sender: Sender agent name
            recipient: Recipient agent name
            content: Message content
            timestamp: Message timestamp
            use_rust: Whether to use the Rust implementation. If None, 
                     automatically detects based on availability and 
                     environment variables.
        """
        self.id = id
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.timestamp = timestamp
        
        # Check if Rust implementation should be used
        if use_rust is None:
            # Check environment variable
            env_setting = os.getenv('CREWAI_RUST_SERIALIZATION', 'auto').lower()
            if env_setting == 'true':
                self._use_rust = True
            elif env_setting == 'false':
                self._use_rust = False
            else:  # 'auto' or other values
                self._use_rust = _RUST_AVAILABLE
        else:
            self._use_rust = use_rust and _RUST_AVAILABLE
        
        # Initialize the appropriate implementation
        if self._use_rust:
            try:
                self._message = _AgentMessage(id, sender, recipient, content, timestamp)
                self._implementation = "rust"
            except Exception as e:
                # Fallback to Python implementation
                self._use_rust = False
                self._message = None
                self._implementation = "python"
                print(f"Warning: Failed to initialize Rust message serialization, falling back to Python: {e}")
        else:
            self._message = None
            self._implementation = "python"
    
    def to_json(self) -> str:
        """
        Serialize the message to JSON.
        
        Returns:
            JSON string representation of the message
        """
        if self._use_rust:
            try:
                return self._message.to_json()
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust serialization failed, using Python fallback: {e}")
                self._use_rust = False
                return self._python_to_json()
        else:
            return self._python_to_json()
    
    def _python_to_json(self) -> str:
        """Python implementation of JSON serialization for fallback."""
        data = {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'content': self.content,
            'timestamp': self.timestamp
        }
        return json.dumps(data, separators=(',', ':'))
    
    @classmethod
    def from_json(cls, json_str: str, use_rust: Optional[bool] = None) -> 'AgentMessage':
        """
        Deserialize a message from JSON.
        
        Args:
            json_str: JSON string representation of the message
            use_rust: Whether to use the Rust implementation
            
        Returns:
            Deserialized AgentMessage instance
        """
        # Check if Rust implementation should be used
        if use_rust is None:
            # Check environment variable
            env_setting = os.getenv('CREWAI_RUST_SERIALIZATION', 'auto').lower()
            if env_setting == 'true':
                use_rust = True
            elif env_setting == 'false':
                use_rust = False
            else:  # 'auto' or other values
                use_rust = _RUST_AVAILABLE
        
        if use_rust and _RUST_AVAILABLE:
            try:
                rust_message = _AgentMessage.from_json(json_str)
                return cls(
                    id=rust_message.id,
                    sender=rust_message.sender,
                    recipient=rust_message.recipient,
                    content=rust_message.content,
                    timestamp=rust_message.timestamp,
                    use_rust=use_rust
                )
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust deserialization failed, using Python fallback: {e}")
        # Python implementation
        data = json.loads(json_str)
        return cls(
            id=data['id'],
            sender=data['sender'],
            recipient=data['recipient'],
            content=data['content'],
            timestamp=data['timestamp'],
            use_rust=False
        )
    
    @property
    def implementation(self) -> str:
        """Get the current implementation type."""
        return self._implementation
    
    def __repr__(self) -> str:
        """String representation of the message."""
        return f"AgentMessage(id={self.id}, sender={self.sender}, recipient={self.recipient})"


class RustSerializer:
    """
    High-performance batch serializer using Rust backend.
    
    This class provides optimized serialization for multiple messages
    with zero-copy optimizations.
    """
    
    def __init__(self, use_rust: Optional[bool] = None):
        """
        Initialize the serializer.
        
        Args:
            use_rust: Whether to use the Rust implementation. If None, 
                     automatically detects based on availability and 
                     environment variables.
        """
        # Check if Rust implementation should be used
        if use_rust is None:
            # Check environment variable
            env_setting = os.getenv('CREWAI_RUST_SERIALIZATION', 'auto').lower()
            if env_setting == 'true':
                self._use_rust = True
            elif env_setting == 'false':
                self._use_rust = False
            else:  # 'auto' or other values
                self._use_rust = _RUST_AVAILABLE
        else:
            self._use_rust = use_rust and _RUST_AVAILABLE
    
    def serialize_batch(self, messages: list) -> list:
        """
        Serialize a batch of messages efficiently.
        
        Args:
            messages: List of message data dictionaries
            
        Returns:
            List of JSON string representations
        """
        if self._use_rust:
            try:
                # Convert to AgentMessage objects and serialize
                serialized_messages = []
                for msg_data in messages:
                    msg = AgentMessage(
                        id=str(msg_data.get('id', '')),
                        sender=str(msg_data.get('sender', '')),
                        recipient=str(msg_data.get('recipient', '')),
                        content=str(msg_data.get('content', '')),
                        timestamp=int(msg_data.get('timestamp', 0)),
                        use_rust=True
                    )
                    serialized_messages.append(msg.to_json())
                return serialized_messages
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust batch serialization failed, using Python fallback: {e}")
                self._use_rust = False
                return self._python_serialize_batch(messages)
        else:
            return self._python_serialize_batch(messages)
    
    def _python_serialize_batch(self, messages: list) -> list:
        """Python implementation of batch serialization for fallback."""
        serialized_messages = []
        for msg_data in messages:
            data = {
                'id': str(msg_data.get('id', '')),
                'sender': str(msg_data.get('sender', '')),
                'recipient': str(msg_data.get('recipient', '')),
                'content': str(msg_data.get('content', '')),
                'timestamp': int(msg_data.get('timestamp', 0))
            }
            serialized_messages.append(json.dumps(data, separators=(',', ':')))
        return serialized_messages
    
    def deserialize_batch(self, json_strings: list) -> list:
        """
        Deserialize a batch of messages efficiently.
        
        Args:
            json_strings: List of JSON string representations
            
        Returns:
            List of message data dictionaries
        """
        if self._use_rust:
            try:
                # Deserialize using Rust implementation
                deserialized_messages = []
                for json_str in json_strings:
                    msg = AgentMessage.from_json(json_str, use_rust=True)
                    msg_data = {
                        'id': msg.id,
                        'sender': msg.sender,
                        'recipient': msg.recipient,
                        'content': msg.content,
                        'timestamp': msg.timestamp
                    }
                    deserialized_messages.append(msg_data)
                return deserialized_messages
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust batch deserialization failed, using Python fallback: {e}")
                self._use_rust = False
                return self._python_deserialize_batch(json_strings)
        else:
            return self._python_deserialize_batch(json_strings)
    
    def _python_deserialize_batch(self, json_strings: list) -> list:
        """Python implementation of batch deserialization for fallback."""
        deserialized_messages = []
        for json_str in json_strings:
            data = json.loads(json_str)
            deserialized_messages.append(data)
        return deserialized_messages