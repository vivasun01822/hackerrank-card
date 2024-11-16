import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import cairosvg
import os


# Fetch user profile data from HackerRank
def fetch_hackerrank_data(username):
    url = f"https://www.hackerrank.com/{username}"
    headers = {
        "User-Agent": os.getenv("HACKERRANK_CARD_USER_AGENT", "HackerRankCardApp")
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("User not found or request failed")

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract profilename from the title
    title = soup.find("title").text.strip()
    profile_name = title.split(" - ")[0] if " - " in title else "N/A"

    # Extract badges
    badges = soup.find_all('div', class_='hacker-badge')
    badge_data = []

    for badge in badges:
        # Extract the badge title, ensuring it defaults to 'N/A' if not found
        badge_title = badge.find('text', class_='badge-title').text.strip() if badge.find('text',
                                                                                          class_='badge-title') else 'N/A'

        # Extract the badge icon URL (SVG or image link)
        badge_icon = badge.find('image', class_='badge-icon')
        badge_icon_url = badge_icon['xlink:href'] if badge_icon and 'xlink:href' in badge_icon.attrs else 'N/A'

        # Fetch data from specific badge IDs (e.g., badge-silver-gradient, badge-star)
        silver_gradient_badge = soup.find(id="badge-silver-gradient")
        star_badge = soup.find(class_="badge-star")

        # Optionally, add more fields like stars, colors, or additional text based on the available HTML structure
        silver_gradient_data = silver_gradient_badge.text.strip() if silver_gradient_badge else 'N/A'
        star_badge_data = star_badge.text.strip() if star_badge else 'N/A'

        # Collect the badge data, including the additional info
        badge_data.append({
            'title': badge_title,
            'icon_url': badge_icon_url,
            'silver_gradient': silver_gradient_data,
            'star_badge': star_badge_data
        })

    # Return the collected badge data
    return {
        "username": username,
        "full_name": profile_name,
        "badges": badge_data
    }


# Convert SVG to PNG
def convert_svg_to_png(svg_url):
    try:
        svg_response = requests.get(svg_url)
        if svg_response.status_code == 200:
            png_image = cairosvg.svg2png(bytestring=svg_response.content)
            return Image.open(BytesIO(png_image))
    except Exception as e:
        print(f"Error converting SVG to PNG: {e}")
    return None


# Load HackerRank logo
def load_local_hackerrank_logo(logo_path):
    if os.path.exists(logo_path):
        return Image.open(logo_path)
    print(f"Logo file not found at {logo_path}")
    return None


def create_github_card(data, logo_path, output_file):
    logo = load_local_hackerrank_logo(logo_path)
    if not logo:
        return

    # Print badge information
    print("Badges Information:")
    for badge in data['badges']:
        print(f"Title: {badge['title']}, Icon URL: {badge['icon_url']}")

    # Card dimensions
    card_width = 600
    logo_height = 80
    badge_width = 50
    space_between_badges = 10
    y_offset_start = logo_height + 20
    y_offset = y_offset_start

    # Calculate number of badges in a row and total rows
    badges_in_row = (card_width - 40) // (badge_width + space_between_badges)
    badge_rows = (len(data['badges']) + badges_in_row - 1) // badges_in_row

    # Increase height for badges and text
    card_height = y_offset_start + badge_rows * (badge_width + space_between_badges + 20) + 180

    # Create card image
    img = Image.new("RGB", (card_width, card_height), color="white")
    draw = ImageDraw.Draw(img)

    # Add the HackerRank logo
    logo_resized = logo.resize((200, logo_height))
    img.paste(logo_resized, (20, 20))

    # Load fonts
    try:
        font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", size=32)
        font_small = ImageFont.truetype("DejaVuSans-Bold.ttf", size=16)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Add username and full name
    draw.text((20, y_offset), f"HackerRank User: {data['username']}", fill="black", font=font_large)
    y_offset += 80
    draw.text((20, y_offset), f"Name: {data['full_name']}", fill="black", font=font_small)
    y_offset += 60

    draw.text((20, y_offset), "Badges:", fill="black", font=font_small)
    y_offset += 40

    # Add badges and titles
    x_offset = 20
    for idx, badge in enumerate(data['badges']):
        if badge['icon_url'] != 'N/A':
            try:
                # Download and process the badge icon
                if badge['icon_url'].endswith('.svg'):
                    icon_image = convert_svg_to_png(badge['icon_url'])
                else:
                    icon_response = requests.get(badge['icon_url'])
                    icon_image = Image.open(
                        BytesIO(icon_response.content)) if icon_response.status_code == 200 else None

                if icon_image:
                    # Resize the icon
                    icon_image = icon_image.resize((badge_width, badge_width))
                    img.paste(icon_image, (x_offset, y_offset))

                    # Add the badge title below the icon
                    title_bbox = draw.textbbox((0, 0), badge['title'], font=font_small)
                    title_width = title_bbox[2] - title_bbox[0]  # Calculate text width
                    text_x = x_offset + badge_width // 2 - title_width // 2
                    draw.text((text_x, y_offset + badge_width + 5), badge['title'], fill="black", font=font_small)

                    # Adjust position for next badge
                    x_offset += badge_width + space_between_badges
                    if (idx + 1) % badges_in_row == 0:
                        x_offset = 20
                        y_offset += badge_width + space_between_badges + 20
            except Exception as e:
                print(f"Failed to download or display badge icon for {badge['title']}: {e}")

    # Save the card
    img.save(output_file)
    print(f"Card saved as {output_file}")


# Main function
if __name__ == "__main__":
    username = "samba9274"  # Replace with actual HackerRank username
    try:
        user_data = fetch_hackerrank_data(username)
        create_github_card(user_data, "hackerrank.jpg", f"{username}_hackerrank_card.png")
    except Exception as e:
        print(f"Error: {e}")