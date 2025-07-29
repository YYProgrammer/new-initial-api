import json
from typing import List, Dict, Any, Optional

class ScreenContentProcessor:
    """
    Processor to extract meaningful text content from screen hierarchy data
    """
    
    def __init__(self):
        pass
    
    def extract_text_content(self, screen_content: str) -> List[Dict[str, Any]]:
        """
        Extract all meaningful text content from screen hierarchy
        
        Args:
            screen_content: JSON string containing screen hierarchy data
            
        Returns:
            List of extracted text items with metadata
        """
        try:
            screen_data = json.loads(screen_content)
            hierarchy = screen_data.get("hierarchy", {})
            
            extracted_texts = []
            self._traverse_hierarchy(hierarchy, extracted_texts, depth=0)
            
            # Filter and prioritize meaningful content
            return self._filter_meaningful_content(extracted_texts)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error processing screen content: {e}")
            return []
    
    def _traverse_hierarchy(self, node: Dict[str, Any], texts: List[Dict[str, Any]], depth: int = 0):
        """
        Recursively traverse the UI hierarchy to extract text content
        """
        if not isinstance(node, dict):
            return
            
        # Extract text from current node attributes
        if 'attributes' in node:
            attrs = node['attributes']
            
            # Extract main text content
            text_content = attrs.get('text', '').strip()
            if text_content and len(text_content) > 1:
                texts.append({
                    'text': text_content,
                    'depth': depth,
                    'type': 'text',
                    'className': attrs.get('className', ''),
                    'resourceId': attrs.get('resourceId', ''),
                    'contentDescription': attrs.get('contentDescription', ''),
                    'clickable': attrs.get('clickable', False)
                })
            
            # Extract content description if meaningful
            content_desc = attrs.get('contentDescription', '').strip()
            if content_desc and len(content_desc) > 2 and content_desc != text_content:
                texts.append({
                    'text': content_desc,
                    'depth': depth,
                    'type': 'description',
                    'className': attrs.get('className', ''),
                    'resourceId': attrs.get('resourceId', ''),
                    'contentDescription': content_desc,
                    'clickable': attrs.get('clickable', False)
                })
        
        # Recurse through children
        if 'children' in node and isinstance(node['children'], list):
            for child in node['children']:
                self._traverse_hierarchy(child, texts, depth + 1)
    
    def _filter_meaningful_content(self, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and prioritize meaningful text content
        """
        if not texts:
            return []
        
        # Remove duplicates and filter meaningless content
        seen_texts = set()
        filtered_texts = []
        
        for item in texts:
            text = item['text']
            
            # Skip if already seen or meaningless
            if (text in seen_texts or 
                len(text) < 2 or 
                text.isspace() or
                text in ['', 'null', 'undefined']):
                continue
                
            seen_texts.add(text)
            filtered_texts.append(item)
        
        # Sort by priority: deeper elements often contain more specific content
        # Also prioritize clickable elements and certain UI components
        def priority_score(item):
            score = 0
            
            # Prefer deeper elements (more specific content)
            score += item['depth'] * 2
            
            # Prefer clickable elements
            if item['clickable']:
                score += 10
                
            # Prefer TextView and Button elements
            if 'TextView' in item['className'] or 'Button' in item['className']:
                score += 5
                
            # Prefer longer text content
            score += min(len(item['text']), 20)
            
            return score
        
        filtered_texts.sort(key=priority_score, reverse=True)
        
        # Return top content items
        return filtered_texts[:20]  # Limit to top 20 items to avoid overwhelming
    
    def get_context_summary(self, screen_content: str) -> str:
        """
        Generate a context summary of the screen content for AI processing
        """
        texts = self.extract_text_content(screen_content)
        
        if not texts:
            return "No meaningful text content found in screen."
        
        # Create a concise summary of the most relevant content
        top_texts = texts[:10]  # Use top 10 most relevant texts
        
        summary_parts = []
        for item in top_texts:
            context = f"Text: '{item['text']}"
            if item['className']:
                context += f" (Type: {item['className'].split('.')[-1]})"
            if item['clickable']:
                context += " [Clickable]"
            context += "'"
            summary_parts.append(context)
        
        return "Screen content includes: " + " | ".join(summary_parts)