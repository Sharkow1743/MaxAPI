import re

def parse_markdown(text):
    """Parses markdown style text to a structured format for later usage.

    Args:
        text (str): The markdown formatted text.

    Returns:
        tuple: A tuple containing:
            - list: List of formatting information (type, offset, length)
            - str: Text without markdown formatting.
    """
    result = []
    
    def process_match(match, md_type):
        actual_offset = match.start() - sum(
            len(m.group(0)) - (len(m.group(1)) if m.group(1) is not None else 0)
            for m in re.finditer(r'\[(.*?)\]\((.*?)\)|\*(.*?)\*|/(.*?)/|_(.*?)_', text[:match.start()])
        )
        
        format = {
            "type": md_type,
            "from": actual_offset,
            "length": len(match.group(1)),
            "attributes": {}
        }
        if md_type == 'LINK':
            format['attributes']['url'] = match.group(2)

        result.append(format)

        return match.group(1)
    
    text = re.sub(r'\[(.*?)\]\((?P<url>.*?)\)', lambda m: process_match(m, "LINK"), text)
    text = re.sub(r'\*(.*?)\*', lambda m: process_match(m, "STRONG"), text)
    # text = re.sub(r'/(.*?)/', lambda m: process_match(m, "ITALIC"), text) # no italic yet
    text = re.sub(r'_(.*?)_', lambda m: process_match(m, "UNDERLINE"), text)
    
    return result, text.strip()
