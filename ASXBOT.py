# Import necessary libraries
from time import time
import subprocess
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException, NoSuchElementException


def get_chromedriver_version():
  """
  This function retrieves the currently installed ChromeDriver version (if any).
  """
  try:
    # Use subprocess to run the chromedriver command and capture its version output
    result = subprocess.run(["chromedriver", "--version"], capture_output=True, text=True)
    version = result.stdout.split()[1]  # Extract the version number from the output
    return version
  except (subprocess.CalledProcessError, FileNotFoundError):
    # Handle cases where chromedriver is not installed or the command fails
    return None

def install_chromedriver_if_needed():
  """
  This function checks the current ChromeDriver version and installs a new one if necessary.
  """
  current_version = get_chromedriver_version()
  if current_version is None or is_chromedriver_old(current_version):
    print("Installing the latest ChromeDriver...")
    ChromeDriverManager().install()
  else:
    print(f"ChromeDriver version {current_version} is up-to-date.")

def is_chromedriver_old(current_version):
  """
  This function checks if the current ChromeDriver version is older than a specified threshold.
  You can adjust the threshold as needed.
  """
  # Adjust the threshold as needed
  old_version_threshold = "129.0.6668.58"  # Replace with your desired threshold

  return current_version < old_version_threshold

# Install ChromeDriver if needed
install_chromedriver_if_needed()

# Set a proper timeout value (e.g., 10 seconds)
wait_time = 10

urls = ['https://www.asx.com.au/markets/trade-our-cash-market/equity-market-prices/',
        # 'https://www.tradingview.com/markets/stocks-australia/market-movers-large-cap/',
        # 'https://www.tradingview.com/markets/stocks-usa/market-movers-active/',
        # 'https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/',
        # 'https://www.tradingview.com/markets/stocks-usa/market-movers-losers/',
        # 'https://www.tradingview.com/markets/stocks-usa/market-movers-most-volatile/',
        # 'https://www.tradingview.com/markets/stocks-usa/market-movers-overbought/',
        # 'https://www.tradingview.com/markets/stocks-usa/market-movers-oversold/'
       ]

url = urls[0]

# Initialize the Chrome WebDriver with the correct timeout
service = Service(ChromeDriverManager().install())  # Install only if not already installed

browser = webdriver.Chrome(service=service, options=webdriver.ChromeOptions())
browser.implicitly_wait(7)
browser.get(url)
browser.maximize_window()

#Get file base name

file_base_name = url.split('/')[-2]
print(file_base_name)
print(f'Scraping {url}...')

# Create an Excel Writer object
xlwriter = pd.ExcelWriter(file_base_name + '.xlsx')

# Find the "Accept All Cookies" button using the given XPath
accept_all_button = WebDriverWait(browser, 3.5).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))

# Click the button
accept_all_button.click()

try:
  # Attempt to find the element quickly to verify presence
  # svg_icon = browser.find_element(By.XPATH, "//svg[@class='svgicon svgicon-plus']")
  # # If found, proceed with WebDriverWait
  view_more_button = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="symbolName" and contains(text(), "VIEW MORE")]')))
  # Click on the SVG icon
  view_more_button.click()
except NoSuchElementException:
  print(f"Error: view_more_button not found")
except TimeoutException:
  print(f"Error: view_more_button icon not clickable after {wait_time} seconds")

# Find the target div element
tables = browser.find_elements(By.XPATH, "//div[@class='col-xs-12 col-sm-6 col-md-4']")

# Create an ExcelWriter object
with pd.ExcelWriter(file_base_name + '.xlsx', engine='xlsxwriter') as writer:
    for table in tables:
        captions = table.find_elements(By.XPATH, ".//caption[@class='header']")
        for caption in captions:
            caption_text = caption.text
            print(caption_text)

            headers = [header.text for header in table.find_elements(By.XPATH, ".//th")]
            rows = []
            for row in table.find_elements(By.XPATH, ".//tr"):
                cells = [cell.text for cell in row.find_elements(By.XPATH, ".//td")]
                rows.append(cells)

            df = pd.DataFrame(rows, columns=headers)

            # Truncate sheet name if too long
            sheet_name = caption_text[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)

browser.quit()
