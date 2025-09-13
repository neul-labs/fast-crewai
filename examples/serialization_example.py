# Example: Replacing Python Serialization with Rust Implementation

# This example shows how we could replace the existing Python serialization
# system with a high-performance Rust implementation

from crewai_rust import AgentMessage
import json
import time

class RustMessageSerializer:
    \"\"\"
    A high-performance message serializer using Rust backend
    \"\"\"
    
    def __init__(self):
        # Track serialization statistics
        self.serialization_times = []
        self.deserialization_times = []
    
    def serialize_to_json(self, message_data):
        \"\"\"
        Serialize message data to JSON using the Rust backend
        \"\"\"
        start_time = time.time()
        
        try:
            # Create an AgentMessage object with the data
            message = AgentMessage(
                id=str(message_data.get('id', '')),
                sender=str(message_data.get('sender', '')),
                recipient=str(message_data.get('recipient', '')),
                content=str(message_data.get('content', '')),
                timestamp=int(message_data.get('timestamp', 0))
            )
            
            # Serialize to JSON using the Rust backend
            json_str = message.to_json()
            
            # Track serialization time
            serialization_time = time.time() - start_time
            self.serialization_times.append(serialization_time)
            
            return json_str
            
        except Exception as e:
            raise Exception(f\"Serialization failed: {str(e)}\")
    
    def deserialize_from_json(self, json_str):
        \"\"\"
        Deserialize message data from JSON using the Rust backend
        \"\"\"
        start_time = time.time()
        
        try:
            # Deserialize from JSON using the Rust backend
            message = AgentMessage.from_json(json_str)
            
            # Convert back to Python dict
            message_data = {
                'id': message.id,
                'sender': message.sender,
                'recipient': message.recipient,
                'content': message.content,
                'timestamp': message.timestamp
            }
            
            # Track deserialization time
            deserialization_time = time.time() - start_time
            self.deserialization_times.append(deserialization_time)
            
            return message_data
            
        except Exception as e:
            raise Exception(f\"Deserialization failed: {str(e)}\")
    
    def serialize_batch(self, messages):
        \"\"\"
        Serialize a batch of messages efficiently
        \"\"\"
        serialized_messages = []
        for message_data in messages:
            json_str = self.serialize_to_json(message_data)
            serialized_messages.append(json_str)
        return serialized_messages
    
    def deserialize_batch(self, json_strings):
        \"\"\"
        Deserialize a batch of messages efficiently
        \"\"\"
        deserialized_messages = []
        for json_str in json_strings:
            message_data = self.deserialize_from_json(json_str)
            deserialized_messages.append(message_data)
        return deserialized_messages
    
    def get_performance_stats(self):
        \"\"\"
        Get detailed performance statistics
        \"\"\"
        stats = {}
        
        if self.serialization_times:
            stats['serialization'] = {
                'total_operations': len(self.serialization_times),
                'average_time': sum(self.serialization_times) / len(self.serialization_times),
                'min_time': min(self.serialization_times),
                'max_time': max(self.serialization_times),
                'total_time': sum(self.serialization_times)
            }
        
        if self.deserialization_times:
            stats['deserialization'] = {
                'total_operations': len(self.deserialization_times),
                'average_time': sum(self.deserialization_times) / len(self.deserialization_times),
                'min_time': min(self.deserialization_times),
                'max_time': max(self.deserialization_times),
                'total_time': sum(self.deserialization_times)
            }
        
        return stats

# Example usage:
if __name__ == \"__main__\":
    # Create a Rust-backed message serializer
    serializer = RustMessageSerializer()
    
    # Create some test messages
    messages = [
        {
            'id': '1',
            'sender': 'agent_1',
            'recipient': 'agent_2',
            'content': 'Hello, how are you?',
            'timestamp': int(time.time())
        },
        {
            'id': '2',
            'sender': 'agent_2',
            'recipient': 'agent_1',
            'content': 'I am doing well, thank you!',
            'timestamp': int(time.time()) + 1
        },
        {
            'id': '3',
            'sender': 'agent_1',
            'recipient': 'agent_3',
            'content': 'Can you help with this task?',
            'timestamp': int(time.time()) + 2
        }
    ]
    
    # Serialize messages
    print(\"Serializing messages...\")
    serialized_messages = serializer.serialize_batch(messages)
    for i, json_str in enumerate(serialized_messages):
        print(f\"Message {i+1}: {json_str}\")
    
    # Deserialize messages
    print(\"\\nDeserializing messages...\")
    deserialized_messages = serializer.deserialize_batch(serialized_messages)
    for i, message_data in enumerate(deserialized_messages):
        print(f\"Message {i+1}: {message_data}\")
    
    # Verify that the data is the same
    print(\"\\nVerifying data integrity...\")
    for original, deserialized in zip(messages, deserialized_messages):
        if original == deserialized:
            print(\"✓ Data integrity verified\")
        else:
            print(\"✗ Data integrity check failed\")
            print(f\"Original: {original}\")
            print(f\"Deserialized: {deserialized}\")
    
    # Print performance statistics
    stats = serializer.get_performance_stats()
    print(f\"\\nPerformance statistics: {stats}\")