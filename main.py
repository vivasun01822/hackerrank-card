import requests

# Function to fetch user stats (badges) from HackerRank
def fetch_badges(username):
    url = f"https://www.hackerrank.com/rest/hackers/{username}/badges"
    headers = {
        "User-Agent": "hackerRankCard"  # Replace with your app's name
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching badges: {e}")
        return None

# Define a model class to represent each badge
class Badge:
    def __init__(self, badge_category, badge_name, current_points, stars, solved, total_challenges, progress_to_next_star, url):
        self.badge_category = badge_category
        self.badge_name = badge_name
        self.current_points = current_points
        self.stars = stars
        self.solved = solved
        self.total_challenges = total_challenges
        self.progress_to_next_star = progress_to_next_star
        self.url = url

    def display(self):
        """Method to display the badge information."""
        print(f"===============================")
        print(f"Badge Name: {self.badge_name}")
        print(f"Category: {self.badge_category}")
        print(f"Current Points: {self.current_points}")
        print(f"Stars: {self.stars}")
        print(f"Solved Challenges: {self.solved}")
        print(f"Total Challenges: {self.total_challenges}")
        print(f"Progress to Next Star: {self.progress_to_next_star * 100:.2f}%")
        print(f"More Info: https://www.hackerrank.com{self.url}")
        print(f"===============================")

# Function to bind response data to Badge objects
def bind_badges_data(response_data):
    badges = []
    if 'models' in response_data:
        for badge_data in response_data['models']:
            # Create a Badge object for each badge in the response
            badge = Badge(
                badge_category=badge_data.get('badge_category', 'N/A'),
                badge_name=badge_data.get('badge_name', 'N/A'),
                current_points=badge_data.get('current_points', 'N/A'),
                stars=badge_data.get('stars', 'N/A'),
                solved=badge_data.get('solved', 'N/A'),
                total_challenges=badge_data.get('total_challenges', 'N/A'),
                progress_to_next_star=badge_data.get('progress_to_next_star', 'N/A'),
                url=badge_data.get('url', '#')
            )
            badges.append(badge)
    return badges

# Function to display badges
def display_badges(badges_data):
    if not badges_data or 'models' not in badges_data:
        print("No badges found for this user.")
        return

    badges = bind_badges_data(badges_data)

    if not badges:
        print("No badges found.")
        return

    for badge in badges:
        badge.display()

# Example usage
username = 'samba9274'  # Replace with the actual HackerRank username
badges_data = fetch_badges(username)

if badges_data:
    display_badges(badges_data)
