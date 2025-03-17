# Grandytojai Web Scraper Documentation

## Overview

This Python script scrapes products from e-commerce websites, specifically from the computer components category. It extracts product models, names, and prices, then saves the data into CSV files.

## Dependencies

The script requires the following Python libraries:

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

Run all the scripts using:

### Windows

```bash
python -m scrapers.skytech
...
```

### Linux

```bash
#Initialise virtual environment
python3 -m venv venv
source venv/bin/activate

python -m scrapers.skytech
...

#Deactivate virtual environment
deactivate
```

## How It Works

### 1. **Initialize a Session**

The script starts by creating a session to handle requests efficiently and defining the target URL:

```python
session = requests.Session()
url = 'https://www.skytech.lt/kompiuteriai-komponentai-kompiuteriu-komponentai-v-85.html?sand=2'
headers = {'User-Agent': 'Mozilla/5.0 ... Safari/537.36'}
```

### 2. **Fetching Category Links**

The script extracts category links from the main page:

- It finds all categories using `ul.visi-catlist`.
- It constructs complete URLs for each category.

### 3. **Extracting Product Data**

For each category link:

- The script fetches the page content.
- Extracts the product model, name, and price.
- Handles pagination if 500 items are listed.
- Organizes the data into a Pandas DataFrame.

### 4. **Saving Data to CSV**

Each category's product data is saved as a CSV file in a structured directory.

## Functions

### `nextPage(url, models, names, prices)`

- Handles pagination by fetching additional product listings when more than 500 products exist on a page.
- Updates the `models`, `names`, and `prices` lists with additional entries.

## Error Handling

- If the request fails, the script prints an error message.
- If the number of extracted models, names, and prices do not match, a warning is displayed.

## Notes

- The script assumes Skytech.lt’s website structure remains unchanged.
- If the HTML structure changes, `class_` attributes may need to be updated in `BeautifulSoup` selectors.

