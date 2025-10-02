from playwright.sync_api import sync_playwright
import csv
import time

# Start Playwright
with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=False)  # Headless mode for faster scraping
    page = browser.new_page()

    # Create CSV file and write header
    csv_filename = "books_data.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Page', 'Book_Number', 'Title', 'Price', 'Rating', 'Image_Link', 'Availability', 'Book_Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        total_books_scraped = 0
        current_page = 1

        # Start with the first page
        page.goto("https://books.toscrape.com/")

        while True:
            print(f"\nScraping page {current_page}...")

            # Wait for page to load
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Additional wait to ensure content is loaded

            # Find the ol tag that contains all book items
            ol_element = page.locator("ol.row")

            # Check if ol element exists on the page
            if ol_element.count() == 0:
                print(f"No books found on page {current_page}. Ending scraping.")
                break

            # Find all li tags within the ol element
            li_elements = ol_element.locator("li")

            # Get the count of li elements
            li_count = li_elements.count()

            if li_count == 0:
                print(f"No books found on page {current_page}. Ending scraping.")
                break

            print(f"Found {li_count} books on page {current_page}")

            # Loop through each li element (book) on current page
            for i in range(li_count):
                book_data = {
                    'Page': current_page,
                    'Book_Number': total_books_scraped + 1,
                    'Title': 'Not found',
                    'Price': 'Not found',
                    'Rating': 'Not found',
                    'Image_Link': 'Not found',
                    'Availability': 'Not found',
                    'Book_Link': 'Not found'
                }

                # Get the current li element
                current_li = li_elements.nth(i)

                # Extract book title
                try:
                    title_element = current_li.locator("h3 a")
                    title = title_element.get_attribute("title")
                    if title:
                        book_data['Title'] = title
                except:
                    pass

                # Extract book price
                try:
                    price_element = current_li.locator("p.price_color")
                    price = price_element.text_content()
                    if price:
                        book_data['Price'] = price.strip()
                except:
                    pass

                # Extract book rating
                try:
                    rating_element = current_li.locator("p.star-rating")
                    rating_class = rating_element.get_attribute("class")
                    if rating_class:
                        rating = rating_class.split()[-1]
                        book_data['Rating'] = rating
                except:
                    pass

                # Extract book image link
                try:
                    img_element = current_li.locator("div.image_container img")
                    img_src = img_element.get_attribute("src")
                    if img_src:
                        if img_src.startswith("media/"):
                            img_link = f"https://books.toscrape.com/{img_src}"
                        else:
                            img_link = img_src
                        book_data['Image_Link'] = img_link
                except:
                    pass

                # Extract book availability
                try:
                    availability_element = current_li.locator("p.instock.availability")
                    availability = availability_element.text_content()
                    if availability:
                        book_data['Availability'] = availability.strip()
                except:
                    pass

                # Extract book link
                try:
                    book_link_element = current_li.locator("h3 a")
                    book_href = book_link_element.get_attribute("href")
                    if book_href:
                        book_link = f"https://books.toscrape.com/catalogue/{book_href}"
                        book_data['Book_Link'] = book_link
                except:
                    pass

                # Print book data line by line
                print(f"Book {total_books_scraped + 1}:")
                print(f"  Title: {book_data['Title']}")
                print(f"  Price: {book_data['Price']}")
                print(f"  Rating: {book_data['Rating']}")
                print(f"  Availability: {book_data['Availability']}")
                print(f"  Image Link: {book_data['Image_Link']}")
                print(f"  Book Link: {book_data['Book_Link']}")
                print("-" * 80)

                # Write book data to CSV
                writer.writerow(book_data)
                total_books_scraped += 1

            print(f"Completed page {current_page} - {li_count} books scraped")

            # Check if there's a "next" button to go to the next page
            next_button = page.locator("li.next a")

            if next_button.count() > 0:
                # Click the next button
                try:
                    next_button.click()
                    current_page += 1
                    time.sleep(2)  # Wait between page loads
                except:
                    print("Could not click next button. Ending scraping.")
                    break
            else:
                print("No more pages found. Scraping completed!")
                break

            # Safety check - stop if we've gone through too many pages (in case of infinite loop)
            if current_page > 25:
                print("Reached maximum page limit. Stopping scraping.")
                break

    print(f"\nScraping completed!")
    print(f"Total books scraped: {total_books_scraped}")
    print(f"Total pages scraped: {current_page}")
    print(f"Data saved to: {csv_filename}")

    # Close browser
    browser.close()