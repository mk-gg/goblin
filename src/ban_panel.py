from html2image import Html2Image
import os
from html import escape
from datetime import datetime, timedelta, timezone

def format_created_date(date):
    """Format date as '23 May 2021'"""
    return date.strftime("%d %B %Y")

def format_joined_date(date):
    """Convert datetime to human-readable time difference"""
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

def produce(profile_image, username, user_id, created_date, joined_date, content_message):
    data = {
        "profile_image": profile_image,
        "username": username,
        "user_id": user_id,
        "created_date": format_created_date(created_date),
        "joined_date": format_joined_date(joined_date),
        "content_message": content_message
    }

    # Get absolute path to the image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    default_image_path = os.path.join(current_dir, 'images', 'error.png')

    # Set profile image with absolute file path
    if data["profile_image"] is None:
        data["profile_image"] = f'file://{default_image_path}'

    print(data['profile_image'])

    # Read the HTML template
    with open('main.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Replace placeholders with escaped values
    for key, value in data.items():
        # Use html.escape() to prevent HTML interpretation
        escaped_value = escape(str(value)) if value is not None else ''
        html_content = html_content.replace(f'{{{{{key}}}}}', escaped_value)

    # Save the modified HTML to a new file
    modified_html_file = 'modified_main.html'
    with open(modified_html_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Now take a screenshot of the modified HTML
    hti = Html2Image(browser_executable='C:\\Users\\Gramps\\AppData\\Local\\Chromium\\Application\\chrome.exe')

    hti.screenshot(
        html_file=modified_html_file, css_file='style.css', save_as='produced.png', size=(735, 186)
    )

def test():
        
    # Data to be inserted into the HTML
    data = {
        "profile_image": None,
        "username": "graceful6951_12321322",
        "user_id": "84600160227950592120",
        "created_date": format_created_date(datetime(2023, 1, 22)),
        "joined_date": format_joined_date(datetime.now() - timedelta(days=9)),
        "content_message": "(I'd recommend you contact ➡[ ##Support Ticket*](https:///\shorter.gg/helpdesk/?@)"
    }

    # Get absolute path to the image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    default_image_path = os.path.join(current_dir,  'files', 'error.png')

    # Set profile image with absolute file path
    if data["profile_image"] is None:
        data["profile_image"] = f'file://{default_image_path}'

    print(data['profile_image'])
    print(default_image_path)

    # Read the HTML template
    with open('src\\files\\template.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Replace placeholders with escaped values
    for key, value in data.items():
        # Use html.escape() to prevent HTML interpretation
        escaped_value = escape(str(value)) if value is not None else ''
        html_content = html_content.replace(f'{{{{{key}}}}}', escaped_value)

    # Save the modified HTML to a new file
    modified_html_file = 'modified_main.html'
    with open(modified_html_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Now take a screenshot of the modified HTML
    hti = Html2Image(browser_executable='C:\\Users\\Gramps\\AppData\\Local\\Chromium\\Application\\chrome.exe')

    hti.screenshot(
        html_file=modified_html_file, css_file='src\\files\\style.css', save_as='ban_card.png', size=(735, 186)
    )

test()