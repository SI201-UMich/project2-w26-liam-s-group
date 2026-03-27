# SI 201 HW4 (Library Checkout System)
# Your name:
# Your student id:
# Your email:
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(base_dir, html_path) if not os.path.isabs(html_path) else html_path
 
    with open(abs_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
 
    listings = []
    seen_ids = set()
 
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        id_match = re.search(r"/rooms/(?:plus/)?(\d+)", href)
        if not id_match:
            continue
 
        listing_id = id_match.group(1)
        if listing_id in seen_ids:
            continue
        seen_ids.add(listing_id)


 
        title = None
 
        # The title lives in the parent div's text, as the first segment
        for container in [link.parent, link.parent.parent if link.parent else None]:
            if not container:
                continue
            parent_text = container.get_text(separator="|", strip=True)
            first_segment = parent_text.split("|")[0].strip()
            if 5 < len(first_segment) < 100 and not first_segment.isdigit():
                title = first_segment
                break
 
        # Fallback: check aria-label on the link itself
        if not title:
            aria = link.get("aria-label", "").strip()
            if aria:
                title = aria.split("|")[0].strip()
 
        if title:
            listings.append((title, listing_id))
 


    return listings
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:

    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
 """
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    html_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")

    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    full_text = soup.get_text(" ", strip=True)

    # ------------------------------------------------------------------
    # Policy Number
    # ------------------------------------------------------------------
    policy_number = "Exempt"

    m = re.search(r'\b(20\d{2}-\d+STR)\b', full_text)
    if m:
        policy_number = m.group(1)
    else:
        m = re.search(r'\b(STR-\d+)\b', full_text)
        if m:
            policy_number = m.group(1)
        elif re.search(r'\bpending\b', full_text, re.IGNORECASE):
            policy_number = "Pending"
        else:
            m = re.search(r'[Pp]olicy number[:\s]+(\d+)', full_text)
            if m:
                policy_number = m.group(1)

    # ------------------------------------------------------------------
    # Host Type
    # ------------------------------------------------------------------
    host_type = "Superhost" if "Superhost" in full_text else "regular"

    # ------------------------------------------------------------------
    # Host Name
    # ------------------------------------------------------------------
    host_name = ""
    m = re.search(
        r'Hosted by\s+([A-Z][a-z]+(?:\s+[Aa]nd\s+[A-Z][a-z]+)?)',
        full_text
    )
    if m:
        host_name = m.group(1).strip()

    # ------------------------------------------------------------------
    # Room Type
    # ------------------------------------------------------------------
    room_type = "Entire Room"

    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = tag.get_text(" ", strip=True).lower()
        if not text:
            continue
        if "private" in text:
            room_type = "Private Room"
            break
        elif "shared" in text:
            room_type = "Shared Room"
            break
        elif " in " in text:
            break

    # Fallback: check <title> and og:title meta
    if room_type == "Entire Room":
        title_tag = soup.find("title")
        og_title = soup.find("meta", property="og:title")
        for candidate_text in [
            title_tag.get_text() if title_tag else "",
            og_title.get("content", "") if og_title else "",
        ]:
            lower = candidate_text.lower()
            if "private" in lower:
                room_type = "Private Room"
                break
            elif "shared" in lower:
                room_type = "Shared Room"
                break

    # ------------------------------------------------------------------
    # Location Rating
    # ------------------------------------------------------------------
    location_rating = 0.0
    m = re.search(r'[Ll]ocation\s+(\d+\.\d+)', full_text)
    if m:
        location_rating = float(m.group(1))

    return {
        listing_id: {
            "policy_number":   policy_number,
            "host_type":       host_type,
            "host_name":       host_name,
            "room_type":       room_type,
            "location_rating": location_rating,
        }
    }
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    sorted_data = sorted(data, key=lambda row: row[6], reverse=True)
    
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Listing Title",
            "Listing ID",
            "Policy Number",
            "Host Type",
            "Host Name",
            "Room Type",
            "Location Rating",
        ])
        for row in sorted_data:
            writer.writerow(row)
   
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(len(self.listings), 18)

        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)