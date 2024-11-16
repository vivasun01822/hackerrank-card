import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import cairosvg
import os


# Function to fetch user profile data from HackerRank
def fetch_hackerrank_data(username):
    url = f"https://www.hackerrank.com/profile/{username}"
    headers = {
        "User-Agent": "hackerRankCard"  # Replace with your app's name
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("User not found or request failed")

    soup = BeautifulSoup(response.text, "html.parser")

    # Extracting profile info from the title tag
    title = soup.find("title").text.strip()
    try:
        profile_name = title.split(" - ")[0]  # Extract the name part before the '-'
    except IndexError:
        profile_name = "N/A"

    # Find all badge elements
    badges = soup.find_all('div', class_='hacker-badge')

    # Iterate through the badges to extract relevant details
    badge_data = []
    for badge in badges:
        badge_title = badge.find('text', class_='badge-title').text if badge.find('text', class_='badge-title') else 'N/A'

        # Check for other possible attributes for image URL
        badge_icon = badge.find('image', class_='badge-icon')
        if badge_icon:
            badge_icon_url = badge_icon['xlink:href'] if 'xlink:href' in badge_icon.attrs else 'N/A'
        else:
            badge_icon_url = 'N/A'

        badge_data.append({'title': badge_title, 'icon_url': badge_icon_url})

    return {
        "username": username,
        "full_name": profile_name,
        "badges": badge_data
    }


# Function to handle SVG to PNG conversion
def convert_svg_to_png(svg_url):
    try:
        # Fetch the SVG content
        svg_response = requests.get(svg_url)
        if svg_response.status_code == 200:
            # Convert the SVG content to PNG using cairosvg
            png_image = cairosvg.svg2png(bytestring=svg_response.content)
            return Image.open(BytesIO(png_image))
        else:
            raise Exception("SVG download failed")
    except Exception as e:
        print(f"Error converting SVG to PNG: {e}")
        return None


# Function to load the HackerRank logo from local storage
def load_local_hackerrank_logo(logo_path):
    if os.path.exists(logo_path):
        return Image.open(logo_path)
    else:
        print(f"Logo file not found at {logo_path}")
        return None


def create_github_card(data, logo_path, output_file):
    # Load the HackerRank logo from local storage
    logo = load_local_hackerrank_logo(logo_path)
    if not logo:
        return

    # Set the width and height for the image
    card_width = 600
    logo_height = 80
    badge_width = 50
    space_between_badges = 10
    y_offset_start = logo_height + 20  # Padding below the logo
    y_offset = y_offset_start

    # Calculate the number of rows needed for badges
    badges_in_row = (card_width - 40) // (badge_width + space_between_badges)
    badge_rows = (len(data['badges']) // badges_in_row) + (1 if len(data['badges']) % badges_in_row != 0 else 0)

    # Increase the overall height to accommodate additional spacing or content
    card_height = y_offset_start + (badge_rows * (badge_width + space_between_badges)) + 140

    # Adding space for name and other text with more padding
    card_height += 80  # Increase the height for user name, badge title, and other text

    # Create a blank image with a white background
    img = Image.new("RGB", (card_width, card_height), color="white")
    draw = ImageDraw.Draw(img)

    # Draw the HackerRank logo
    logo_resized = logo.resize((200, logo_height))  # Resize the logo
    img.paste(logo_resized, (20, 20))  # Position logo at the top

    # Load fonts
    try:
        font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", size=32)
        font_small = ImageFont.truetype("DejaVuSans-Bold.ttf", size=24)
    except IOError:
        print("Error loading font. Make sure the font file exists.")
        return

    # Add text to the image
    draw.text((20, y_offset), f"HackerRank User: {data['username']}", fill="black", font=font_large)
    y_offset += 80  # Increase offset after user info
    draw.text((20, y_offset), f"Name: {data['full_name']}", fill="black", font=font_small)
    y_offset += 60  # Increase offset after name text

    draw.text((20, y_offset), f"Badges:", fill="black", font=font_small)
    y_offset += 60  # Increase offset after badges title

    # Horizontal layout: Initialize x_offset and y_offset for badges
    x_offset = 20

    for idx, badge in enumerate(data['badges']):
        # If badge icon URL is valid
        if badge['icon_url'] != 'N/A':
            try:
                # Check if the icon is an SVG
                if badge['icon_url'].endswith('.svg'):
                    icon_image = convert_svg_to_png(badge['icon_url'])
                else:
                    icon_response = requests.get(badge['icon_url'])
                    if icon_response.status_code == 200:
                        icon_image = Image.open(BytesIO(icon_response.content))

                # If icon image is successfully fetched and processed
                if icon_image:
                    # Resize the icon to fit within the card
                    icon_image = icon_image.resize((badge_width, badge_width))

                    # Paste the badge icon directly onto the card
                    img.paste(icon_image, (x_offset, y_offset))  # Position the icon on the card

                    # Update x_offset for the next badge
                    x_offset += badge_width + space_between_badges

                    # If we've reached the end of the row, move to the next row
                    if (idx + 1) % badges_in_row == 0:
                        x_offset = 20  # Reset x_offset to the start of the next row
                        y_offset += badge_width + space_between_badges  # Move to the next line
            except Exception as e:
                print(f"Failed to download or display badge icon for {badge['title']}: {e}")

    # Save the final image
    img.save(output_file)
    print(f"Card saved as {output_file}")



# Main function
if __name__ == "__main__":
    username = "samba9274"  # Replace with the actual HackerRank username
    try:
        user_data = fetch_hackerrank_data(username)
        create_github_card(user_data, "hackerrank.jpg", f"{username}_hackerrank_card.png")
    except Exception as e:
        print(f"Error: {e}")