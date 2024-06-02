# Job Offers Web Scraper

This Python script is a web scraper for job offer listings. It scrapes job listings, logs any exceptions to a text log file, and saves the results to a CSV file.

## Features

- Scrapes job listings from the specified job offers portal.
- Logs exceptions to a text log file.
- Saves the scraped data to a CSV file.
- Uses a requirements file to manage dependencies.

## Requirements

- Python 3.7 or higher
- `requests` library
- `beautifulsoup4` library
- `pandas` library

## Installation

1. Clone this repository to your local machine.

   ```bash
   git clone https://github.com/MOrgacki/selenium-joboffer-webscraper.git
   ```

2. Navigate to the project directory.

   ```bash
   cd job-offers-scraper
   ```

3. Create a virtual environment.

   ```bash
   python3 -m venv venv
   ```

4. Activate the virtual environment.

   On Windows:

   ```bash
   venv\Scripts\activate
   ```

   On macOS and Linux:

   ```bash
   source venv/bin/activate
   ```

5. Install the required dependencies.

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the script.

   ```bash
   python main.py
   ```

2. The script will create a CSV file named `temp.csv` in the project directory with the scraped job listings.

3. Any exceptions encountered during the scraping process will be logged in a file named `*.txt` in the project directory.

## Configuration

You can configure the following parameters in the `config.ini` file:

```
[APP]
URL = https://www.pracuj.pl/pracuj
LOGIN_URL = https://login.pracuj.pl

[AUTH]
USERNAME = FILL_USERNAME
PASSWORD = FILL_PASSWORD

[LOGS]
ERRORS = logs/errors.log
COMPANY_INFO = logs/info.log

[MOCKS]
STATIC_FOLDER = mocks/mock_offers_page.html

[FILES]
TEMP = temp.csv
RESULT = sklepy_erekruter.csv
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project uses the [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library for web scraping.
- The [pandas](https://pandas.pydata.org/) library is used for data manipulation and CSV file generation.

---

Feel free to contribute to this project by opening issues and submitting pull requests. For major changes, please open an issue first to discuss what you would like to change.

Happy scraping!
