import json
import re

def parse_message_block(lines):
    """Parse a single message block into a dictionary."""
    message_dict = {}
    content_lines = []
    in_code_block = False
    
    for line in lines:
        line = line.strip()
        if line == "```":
            in_code_block = not in_code_block
            continue
        if not line:
            continue
        
        if in_code_block:
            content_lines.append(line)
        else:
            # Handle key-value pairs outside code blocks
            if ":" in line:
                key, value = [part.strip() for part in line.split(":", 1)]
                # Remove trailing comma if present
                if value.endswith(","):
                    value = value[:-1]
                message_dict[key] = value
    
    # Process message content
    if content_lines:
        message_content = parse_code_block(content_lines)
        message_dict["message"] = {"content": message_content}
    elif "message" in message_dict:
        message_dict["message"] = message_dict["message"]
    
    return message_dict

def parse_code_block(lines):
    """Parse login/password pairs from a code block."""
    content = []
    current_entry = {}
    
    for line in lines:
        if line.startswith("Login:"):
            if current_entry:
                content.append(current_entry)
            current_entry = {"login": line.split(":", 1)[1].strip()}
        elif line.startswith("Password:"):
            current_entry["password"] = line.split(":", 1)[1].strip()
    if current_entry:
        content.append(current_entry)
    
    return content

def refactor_file(input_file, output_file):
    """Refactor the input file into structured JSON."""
    with open(input_file, "r") as f:
        lines = f.readlines()
    
    messages = []
    current_block = []
    standalone_text = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("{"):
            if current_block:
                messages.append(parse_message_block(current_block))
            current_block = [line[1:]]  # Remove opening brace
        elif line.startswith("}"):
            current_block.append(line[:-1])  # Remove closing brace
            message = parse_message_block(current_block)
            if standalone_text:
                if "message" in message and isinstance(message["message"], dict):
                    message["message"]["server"] = standalone_text
                standalone_text = None
            messages.append(message)
            current_block = []
        elif line and not line.startswith("```") and not current_block:
            standalone_text = line
        elif current_block:
            current_block.append(line)
    
    # Write to output file
    with open(output_file, "w") as f:
        json.dump(messages, f, indent=2)

# Example usage
input_file = "input.txt"
output_file = "output.json"
refactor_file(input_file, output_file)
print(f"Refactored JSON written to {output_file}")
