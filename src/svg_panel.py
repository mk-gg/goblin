from enum import Enum
import html
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import textwrap
import re
import emoji
import urllib.request
import urllib.error
import cairosvg

def ensure_timezone(dt):
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

@dataclass
class MockMember:
    name: str
    id: int
    guild: str
    created_at: datetime
    joined_at: datetime
    avatar_url: Optional[str] = None

@dataclass
class SeparatorStyle:
    color: str = "#404040"
    width: int = 1
    length: int = 120
    rounded: bool = True
    margin_top: int = 40
    margin_bottom: int = 40

class TextProcessingMode(Enum):
    RAW = "raw"  # No processing, display text as-is
    BASIC = "basic"  # Basic sanitization only
    FULL = "full"  # Full processing (mentions, channels, links)

class ModernWarningPanelGenerator:
    DEFAULT_THEME = {
        'background': '#1F1F1F',
        'text_primary': '#D3C2C3',
        'text_secondary': '#A29696',
        'text_muted': '#404040',
        'separator': '#404040',
        'font_family': 'ui-monospace, monospace',
        'link_color': '#60A5FA'
    }

    DEFAULT_AVATAR = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAeklEQVR4nMWUSwqAMAwFc4a5/0HdKS7qQszPps2DLPqZDjQQkZ0BzlFLWHYKCIrIMNsEooAY9eb7BRXrJ9ofAsddifV3L7KN1eIKpChEBZ44zLUJ/qZPgCFi5s5ywWxTR6anKcZeapqWCwiCONNUfW+5QKKHRsJcteACOPYHCF1Ci4cAAAAASUVORK5CYII="

    def __init__(
        self,
        width: int = 800,
        height: int = 200,
        theme: Optional[dict] = None,
        separator_style: Optional[SeparatorStyle] = None,
        text_processing: TextProcessingMode = TextProcessingMode.FULL
    ):
        
        self.text_processing = text_processing

        self.width = width
        self.height = height
        self.theme = {**self.DEFAULT_THEME, **(theme or {})}
        self.separator_style = separator_style or SeparatorStyle()
        
        # Dynamic spacing based on dimensions
        self.vertical_spacing = height * 0.1
        self.horizontal_spacing = width * 0.025
        
        # Avatar dimensions
        self.avatar_size = min(height * 0.4, 80)  # Responsive avatar size
        self.avatar_margin = self.horizontal_spacing
        
        # Padding and spacing
        self.padding = 20
        
        # Text constraints
        self.max_message_chars = 200
        self.max_font_size = 14
        self.min_font_size = 8
        
        # Calculate sections width
        self.left_section_width = (self.width / 2) - self.padding * 2
        self.right_section_width = (self.width / 2) - self.padding * 2
        
        # Calculate username space
        self.username_start_x = self.avatar_size + self.avatar_margin + self.padding
        self.username_max_width = (self.width / 2) - self.username_start_x - self.padding * 2
        
        # Text wrapping
        self.max_username_chars = int(self.username_max_width / 11)
        self.chars_per_line = int(self.right_section_width / 8)

   
    def _calculate_vertical_positions(self):
        """Calculate vertical positions for all elements."""
        vertical_center = (self.height - self.avatar_size) / 2
        return {
            'avatar_y': vertical_center,
            'name_y': vertical_center + 5,
            'id_y': vertical_center + 25,
            'created_y': vertical_center + 60,
            'member_since_y': vertical_center + 80
        }

    def _create_default_avatar(self, vertical_center: float) -> str:
        """Create a fallback avatar with proper centering."""
        circle_cx = 20 + (self.avatar_size / 2)
        circle_cy = vertical_center + (self.avatar_size / 2)
        return f'''
        <circle 
            cx="{circle_cx}" 
            cy="{circle_cy}" 
            r="{self.avatar_size/2}" 
            fill="{self.theme['text_muted']}"
        />
        <image
            x="20"
            y="{vertical_center}"
            width="{self.avatar_size}"
            height="{self.avatar_size}"
            href="{self.DEFAULT_AVATAR}"
            clip-path="url(#avatar-clip)"
            style="opacity: 1"
        />
        '''

    def _calculate_font_size(self, message: str) -> int:
        length = len(message)
        if length <= 100:
            return self.max_font_size
        elif length <= 130:
            return max(12, self.min_font_size)
        elif length <= 160:
            return max(10, self.min_font_size)
        else:
            return self.min_font_size

    def _sanitize_text(self, text: str) -> str:
        text = html.escape(text)
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;',
            '&': '&amp;'
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text.encode('ascii', 'xmlcharrefreplace').decode('ascii')
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text and add ellipsis if it exceeds max_length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-1] + "…"
    

    def _wrap_text(self, text: str, font_size: int) -> List[str]:
        """Wrap text based on font size and available width."""
        # Adjust chars per line based on font size
        chars_per_line = int(self.right_section_width / (font_size * 0.6))
        return textwrap.wrap(text[:self.max_message_chars], width=chars_per_line)
    

    def _format_time_difference(self, date: datetime) -> str:
        """Format time difference in a human-readable format."""
        now = datetime.now(timezone.utc)
        
        # Ensure the input date is timezone-aware
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        
        diff = now - date
        
        if diff.days >= 365:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''}"
        if diff.days >= 30:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''}"
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''}"
        if diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
        if diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} min{'s' if minutes != 1 else ''}"
        return f"{diff.seconds} second{'s' if diff.seconds != 1 else ''}"
    
    def _process_message_elements(self, message: str) -> List[dict]:
        """
        Process message into renderable elements, preserving mentions, links, and formatting.
        Returns a list of dictionaries containing element type and content.
        """
        elements = []
        current_pos = 0
        
        # Regular expressions for different elements
        mention_pattern = r'<@!?(\d+)>'
        channel_pattern = r'<#(\d+)>'
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        while current_pos < len(message):
            # Check for mentions
            mention_match = re.search(mention_pattern, message[current_pos:])
            channel_match = re.search(channel_pattern, message[current_pos:])
            link_match = re.search(link_pattern, message[current_pos:])
            
            if mention_match and (not channel_match or mention_match.start() < channel_match.start()) and (not link_match or mention_match.start() < link_match.start()):
                # Add text before mention
                if mention_match.start() > 0:
                    elements.append({
                        'type': 'text',
                        'content': message[current_pos:current_pos + mention_match.start()]
                    })
                
                # Add mention
                elements.append({
                    'type': 'mention',
                    'content': f'@user{mention_match.group(1)[-4:]}',
                    'color': self.theme['link_color']
                })
                
                current_pos += mention_match.end()
                
            elif channel_match and (not link_match or channel_match.start() < link_match.start()):
                # Add text before channel
                if channel_match.start() > 0:
                    elements.append({
                        'type': 'text',
                        'content': message[current_pos:current_pos + channel_match.start()]
                    })
                
                # Add channel
                elements.append({
                    'type': 'channel',
                    'content': f'#channel{channel_match.group(1)[-4:]}',
                    'color': self.theme['link_color']
                })
                
                current_pos += channel_match.end()
                
            elif link_match:
                # Add text before link
                if link_match.start() > 0:
                    elements.append({
                        'type': 'text',
                        'content': message[current_pos:current_pos + link_match.start()]
                    })
                
                # Add link
                elements.append({
                    'type': 'link',
                    'content': link_match.group(1),
                    'url': link_match.group(2),
                    'color': self.theme['link_color']
                })
                
                current_pos += link_match.end()
                
            else:
                # Add remaining text
                elements.append({
                    'type': 'text',
                    'content': message[current_pos:]
                })
                break
        
        return elements
    
    def _create_message_text(self, message: str, x: int, y: int) -> str:
        """Create wrapped text elements based on text processing mode."""
        font_size = self._calculate_font_size(message)
        
        # Fixed starting position, just below 'sent message'
        message_start_y = 55  # Adjusted from 55 to create more space
        
        # Reduce available width to prevent text from extending beyond panel
        available_width = self.right_section_width - 20  # Add 20px margin
        
        if self.text_processing == TextProcessingMode.RAW:
            return self._create_raw_text(message, x, message_start_y, font_size, available_width)
        elif self.text_processing == TextProcessingMode.BASIC:
            return self._create_basic_text(message, x, message_start_y, font_size, available_width)
        else:  # TextProcessingMode.FULL
            return self._create_processed_text(message, x, message_start_y, font_size, available_width)
        
    def _break_long_word(self, word: str, max_width: float, font_size: float) -> List[str]:
        """Break a long word into parts that fit within the maximum width."""
        chars_per_segment = int(max_width / (font_size * 0.6))
        segments = []
        
        # Handle emoji separately
        if emoji.is_emoji(word):
            return [word]
            
        # Add hyphen for broken words, leaving space for it
        chars_per_segment = max(1, chars_per_segment - 1)
        
        for i in range(0, len(word), chars_per_segment):
            segment = word[i:i + chars_per_segment]
            # Add hyphen if this isn't the last segment
            if i + chars_per_segment < len(word):
                segment += '-'
            segments.append(segment)
            
        return segments
        
    def _create_raw_text(self, message: str, x: int, y: int, font_size: float, available_width: float) -> str:
        """Create text elements with minimal processing and word breaking for long words."""
        escaped_message = html.escape(message)
        words = escaped_message.split()
        lines = []
        current_line = []
        line_width = 0
        
        for word in words:
            word_width = len(emoji.demojize(word)) * (font_size * 0.6)
            
            if word_width > available_width:
                # If we have accumulated words, add them as a line
                if current_line:
                    lines.append(current_line)
                    current_line = []
                    line_width = 0
                
                # Break the long word
                segments = self._break_long_word(word, available_width, font_size)
                for segment in segments:
                    lines.append([segment])
            
            elif line_width + word_width > available_width:
                lines.append(current_line)
                current_line = [word]
                line_width = word_width
            else:
                current_line.append(word)
                line_width += word_width + (font_size * 0.3)
        
        if current_line:
            lines.append(current_line)
        
        text_elements = []
        current_y = y
        
        for line in lines:
            line_element = f'<text x="{x}" y="{current_y}" fill="{self.theme["text_primary"]}" font-size="{font_size}" font-family="{self.theme["font_family"]}">'
            for word in line:
                if emoji.is_emoji(word):
                    line_element += f'<tspan font-family="Apple Color Emoji,Segoe UI Emoji,Noto Color Emoji,Android Emoji,EmojiSymbols">{word}</tspan>'
                else:
                    line_element += word
                line_element += ' '
            line_element += '</text>'
            text_elements.append(line_element)
            current_y += font_size * 1.4
        
        return '\n'.join(text_elements)
    
    def _create_basic_text(self, message: str, x: int, y: int, font_size: float, available_width: float) -> str:
        """Create text elements with basic sanitization and word breaking for long words."""
        sanitized_message = self._sanitize_text(message)
        words = sanitized_message.split()
        lines = []
        current_line = []
        line_width = 0
        
        for word in words:
            word_width = len(word) * (font_size * 0.6)
            
            if word_width > available_width:
                # If we have accumulated words, add them as a line
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = []
                    line_width = 0
                
                # Break the long word
                segments = self._break_long_word(word, available_width, font_size)
                for segment in segments:
                    lines.append(segment)
            
            elif line_width + word_width > available_width:
                lines.append(' '.join(current_line))
                current_line = [word]
                line_width = word_width
            else:
                current_line.append(word)
                line_width += word_width + (font_size * 0.3)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        text_elements = []
        current_y = y
        
        for line in lines:
            text_elements.append(f'''
                <text x="{x}" y="{current_y}"
                    fill="{self.theme['text_primary']}"
                    font-size="{font_size}"
                    font-family="{self.theme['font_family']}">
                    {line}
                </text>
            ''')
            current_y += font_size * 1.4
        
        return '\n'.join(text_elements)

    def _create_processed_text(self, message: str, x: int, y: int, font_size: float, available_width: float) -> str:
        """Create text elements with full processing and word breaking for long words."""
        elements = self._process_message_elements(message)
        
        text_elements = []
        current_y = y
        line_height = font_size * 1.4
        current_line = []
        line_width = 0
        
        for element in elements:
            content = element['content']
            words = content.split()
            
            for word in words:
                word_width = len(word) * (font_size * 0.6)
                
                if word_width > available_width:
                    # Render current line if exists
                    if current_line:
                        text_elements.append(self._render_text_line(
                            current_line,
                            x,
                            current_y,
                            font_size,
                            available_width
                        ))
                        current_line = []
                        line_width = 0
                        current_y += line_height
                    
                    # Break the long word
                    segments = self._break_long_word(word, available_width, font_size)
                    for segment in segments:
                        text_elements.append(self._render_text_line(
                            [{
                                'type': element['type'],
                                'content': segment,
                                'color': element.get('color', self.theme['text_primary'])
                            }],
                            x,
                            current_y,
                            font_size,
                            available_width
                        ))
                        current_y += line_height
                
                elif line_width + word_width > available_width:
                    # Render current line
                    text_elements.append(self._render_text_line(
                        current_line,
                        x,
                        current_y,
                        font_size,
                        available_width
                    ))
                    current_line = []
                    line_width = 0
                    current_y += line_height
                    
                    # Add word to new line
                    current_line.append({
                        'type': element['type'],
                        'content': word,
                        'color': element.get('color', self.theme['text_primary'])
                    })
                    line_width = word_width + (font_size * 0.3)
                
                else:
                    current_line.append({
                        'type': element['type'],
                        'content': word,
                        'color': element.get('color', self.theme['text_primary'])
                    })
                    line_width += word_width + (font_size * 0.3)
        
        # Render last line
        if current_line:
            text_elements.append(self._render_text_line(
                current_line,
                x,
                current_y,
                font_size,
                available_width
            ))
        
        return '\n'.join(text_elements)

    def _render_text_line(self, line_elements: List[dict], x: float, y: float, font_size: float, available_width: float) -> str:
        """Render a single line of text with mixed elements and constrained width."""
        current_x = x
        elements = []
        
        for element in line_elements:
            content = self._sanitize_text(element['content'])
            element_width = len(content) * (font_size * 0.6)
            
            # Check if adding this element would exceed available width
            if current_x - x + element_width > available_width:
                break
                
            if element['type'] in ['mention', 'channel', 'link']:
                elements.append(f'''
                    <text x="{current_x}" y="{y}"
                        fill="{element['color']}"
                        font-size="{font_size}"
                        font-family="{self.theme['font_family']}"
                        text-decoration="underline">
                        {content}
                    </text>
                ''')
            else:
                elements.append(f'''
                    <text x="{current_x}" y="{y}"
                        fill="{self.theme['text_primary']}"
                        font-size="{font_size}"
                        font-family="{self.theme['font_family']}">
                        {content}
                    </text>
                ''')
            
            current_x += element_width + (font_size * 0.3)
        
        return ''.join(elements)
    

    def get_valid_avatar_url(self, url: str) -> str:
        if not url:
            return ""
        
        if url is None:
            return ""
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            print(f"Invalid URL format: {url}")
            return ""
        

        try:
            request = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}  # Some servers block requests without User-Agent
            )
            urllib.request.urlopen(request)
            return url
        except urllib.error.HTTPError as e:
            # print(f"Cannot access avatar at {url}. HTTP Error: {e.code}")
            return ""
        except urllib.error.URLError as e:
            # print(f"Cannot access avatar at {url}. URL Error: {e.reason}")
            return ""
        except Exception as e:
            # print(f"Error: {e}")
            return ""
    

    def _create_separator(self) -> str:
        """Create a customized separator with optional rounded edges."""
        center_x = self.width / 2
        start_y = self.separator_style.margin_top
        end_y = self.height - self.separator_style.margin_bottom

        if self.separator_style.rounded:
            return f'''
                <path
                    d="M {center_x} {start_y} L {center_x} {end_y}"
                    stroke="{self.separator_style.color}"
                    stroke-width="{self.separator_style.width}"
                    stroke-linecap="round"
                />
            '''
        else:
            return f'''
                <line
                    x1="{center_x}"
                    y1="{start_y}"
                    x2="{center_x}"
                    y2="{end_y}"
                    stroke="{self.separator_style.color}"
                    stroke-width="{self.separator_style.width}"
                />
            '''
        
    def _validate_avatar_url(self, url: Optional[str]) -> Optional[str]:
        """Robust URL validation with comprehensive checks."""
        if not url:
            return None
        
        if url is None:
            return None
        
        


        allowed_prefixes = ['http://', 'https://', 'data:image/']
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', 'data:image/']


        if not any(url.startswith(prefix) for prefix in allowed_prefixes):
            return None


        if not any(url.lower().endswith(ext) or ext in url for ext in valid_extensions):
            return None

        url = url.replace('<', '').replace('>', '')

        
        return self._sanitize_text(url)
    
    def generate_svg(self, data: dict) -> str:
        """Generate SVG content with dynamic data."""
        member_since = self._format_time_difference(data['member'].joined_at)
        created_at = data['member'].created_at.strftime("%d %b %Y")
        truncated_name = self._truncate_text(data['member'].name, self.max_username_chars)
        avatar_url = self._validate_avatar_url(data["member"].avatar_url)
        new_avatar_url = self.get_valid_avatar_url(avatar_url)
        avatar_url = new_avatar_url
        
        # Calculate vertical positions
        positions = self._calculate_vertical_positions()

        svg_content = f'''
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">
                        <defs>
                            <clipPath id="avatar-clip">
                                <circle 
                                    cx="{20 + (self.avatar_size/2)}" 
                                    cy="{positions['avatar_y'] + (self.avatar_size/2)}" 
                                    r="{self.avatar_size/2}"
                                />
                            </clipPath>
                        </defs>
                <!-- Background -->
                <rect 
                    x="0" 
                    y="0" 
                    width="{self.width}" 
                    height="{self.height}" 
                    fill="{self.theme['background']}" 
                    rx="8"
                />

                <!-- Profile Section -->
                <g transform="translate({self.padding}, 0)">
                    <!-- ... [Avatar part] ... -->
                    {
                        f'<image x="20" y="{positions["avatar_y"]}" width="{self.avatar_size}" height="{self.avatar_size}" href="{avatar_url}" clip-path="url(#avatar-clip)" preserveAspectRatio="xMidYMid slice"/>'
                        if avatar_url
                        else self._create_default_avatar(positions['avatar_y'])
                    }
                    <!-- User Info -->
                    <text x="{self.username_start_x}" y="{positions['name_y']}" fill="{self.theme['text_primary']}" font-size="14" font-family="{self.theme['font_family']}">
                        {self._sanitize_text(truncated_name)}
                    </text>
                    <text x="{self.username_start_x}" y="{positions['id_y']}" fill="{self.theme['text_secondary']}" font-size="12.8" font-family="{self.theme['font_family']}">
                        {data['member'].id}
                    </text>
                    <text x="{self.username_start_x}" y="{positions['created_y']}" fill="{self.theme['text_muted']}" font-size="12.8" font-family="{self.theme['font_family']}">
                        Created {created_at}
                    </text>
                    <text x="{self.username_start_x}" y="{positions['member_since_y']}" fill="{self.theme['text_muted']}" font-size="12.8" font-family="{self.theme['font_family']}">
                        Member since {member_since}
                    </text>
                </g>
                {self._create_separator()}

                <!-- Message Section with Dynamic Font Size -->
                <g transform="translate({self.width/2 + self.padding}, {self.padding})">
                    <text fill="{self.theme['text_muted']}" font-size="12.8" x="0" y="35" font-family="{self.theme['font_family']}">
                        sent message
                    </text>
                    {self._create_message_text(data['message'], 0, 55)}
                </g>
            </svg>
        '''
        return svg_content  # Remove .strip() to avoid the syntax error # Remove .strip() to avoid the syntax error

def save_as_png(svg_content: str, output_path: str) -> None:
    """Save SVG content as PNG using cairosvg."""
    try:
        cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=output_path, unsafe=True)
        print(f"Successfully saved PNG to: {output_path}")
    except ImportError:
        raise ImportError("cairosvg is required for PNG export. Please install it with: pip install cairosvg")

def create_modern_warning_panel(
    message: str,
    member: object,
    output_path: str,
    width: int = 800,
    height: int = 200,
    theme: Optional[dict] = None,
    separator_style: Optional[SeparatorStyle] = None,
    text_processing: TextProcessingMode = TextProcessingMode.FULL
) -> None:
    """Create a modern-styled warning panel and save as PNG."""
    panel_data = {
        'message': message,
        'member': member
    }
    
    generator = ModernWarningPanelGenerator(
        width=width,
        height=height,
        theme=theme,
        separator_style=separator_style,
        text_processing=text_processing
    )
    svg_content = generator.generate_svg(panel_data)
    save_as_png(svg_content, output_path)


# Example usage
if __name__ == "__main__":
    test_member = MockMember(
        name="charles45yn0835_38942",
        id=1185466905251827743,
        guild="Ronin Network",
        created_at=datetime(2023, 1, 22),
        joined_at=datetime.now() - timedelta(days=9),
        avatar_url="https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg"
    )

    
    
    custom_theme = {
        'background': '#121212',
        'text_primary': '#D3C2C3',
        'text_secondary': '#A29696',
        'text_muted': '#404040',
        'separator': '#0c0c0c',
        'font_family': 'Roboto mono',
        'link_color': '#60A5FA'
    }
    
    custom_separator = SeparatorStyle(
        color="#0c0c0c",
        width=8,
        length=900,
        rounded=True,
        margin_top=20,
        margin_bottom=20
    )
    
    try:
        create_modern_warning_panel(
            message="If you have any questions or request or enquiries , Create a ticket https://discord.gg/bkn3rE6e ",
            member=test_member,
            output_path="modern_warning_panel.png",
            width=700,
            height=200,
            theme=custom_theme,
            separator_style=custom_separator,
            text_processing=TextProcessingMode.RAW
        )
        
    except Exception as e:
        print(f"Error creating panel: {str(e)}")
        raise