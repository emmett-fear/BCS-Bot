import requests, re, time
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info, warn

URL = "https://masseyratings.com/cf/fbs/ratings"
OUT = "data/2025/week05/massey.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent":"bcs-sim (contact: you@example.com)"}

def parse_with_selenium():
    """Try to scrape with Selenium for dynamic content"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={UA['User-Agent']}")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(URL)
        
        # Wait for the data to load (look for table rows)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
        
        # Additional wait for dynamic content
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, "lxml")
        driver.quit()
        
        teams = []
        for i, tr in enumerate(soup.select("table tr")):
            tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if len(tds) < 2: continue
            
            # Skip header rows
            if i == 0 or tds[0].startswith('Correlation') or tds[0].startswith('College Football'):
                continue
                
            # First cell contains team name (before newline)
            team_name = tds[0].split('\n')[0].strip()
            if team_name:
                teams.append({
                    "rank": len(teams) + 1,
                    "team": canon(team_name)
                })
        
        if teams:
            info(f"Massey: Scraped {len(teams)} teams with Selenium")
            return teams
        else:
            warn("Massey: No teams found with Selenium")
            return []
            
    except ImportError:
        warn("Massey: Selenium not available, falling back to requests")
        return []
    except Exception as e:
        warn(f"Massey: Selenium failed: {e}")
        return []

def parse():
    # First try the dynamic approach with Selenium
    teams = parse_with_selenium()
    
    # If that fails, try the simple approach
    if not teams:
        try:
            r = requests.get(URL, headers=UA, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")
            
            # Look for any data in the page
            for tr in soup.select("table tr"):
                tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
                if len(tds) < 2: continue
                if not re.fullmatch(r"\d+", tds[0]): continue
                rank = int(tds[0])
                team = canon(tds[1])
                teams.append({"rank": rank, "team": team})
                
            if teams:
                info(f"Massey: Scraped {len(teams)} teams with requests")
            else:
                warn("Massey: No data found with requests")
        except Exception as e:
            warn(f"Massey: Requests failed: {e}")
            teams = []
    
    write_json(OUT, comp_payload("massey", WEEK_TAG, teams))

if __name__ == "__main__":
    parse()


