import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

def setup_driver():
    """Set up and return the WebDriver with appropriate options"""
    chrome_options = Options()
    # Uncomment the next line to run in headless mode (no browser window)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def initialize_form(driver):
    """Fill in the initial form fields and checkboxes"""
    # Wait for page to fully load
    time.sleep(3)
    
    try:
        # Select employee count
        employee_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "MAIL[q2]"))
        )
        Select(employee_dropdown).select_by_visible_text("1-5名")
        print("✓ Selected employee count")
        
        # Select industry
        industry_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "MAIL[q27]"))
        )
        Select(industry_dropdown).select_by_visible_text("建設業")
        print("✓ Selected industry")
        
        # Check company status boxes using labels for better clickability
        company_status_paths = [
            "//label[contains(.,'雇用保険、社会保険に加入している')]",
            "//label[contains(.,'追加残業未払い・会社都合解雇など、労務違反をしていない')]",
            "//label[contains(.,'ここ５年で事業承継をした')]"
        ]
        
        for xpath in company_status_paths:
            try:
                label = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", label)
                print(f"✓ Checked: {xpath}")
                time.sleep(0.5)
            except Exception as e:
                print(f"Error checking company status box {xpath}: {e}")
        
        return True
    except Exception as e:
        print(f"Error during form initialization: {e}")
        return False

def get_subsidy_details(driver):
    """Extract subsidy details from the results page"""
    subsidies = []
    
    try:
        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "subsidy"))
        )
        
        # Find all subsidy blocks
        subsidy_articles = driver.find_elements(By.TAG_NAME, "article")
        
        if not subsidy_articles:
            print("No subsidy articles found on the results page.")
            return subsidies
        
        print(f"Found {len(subsidy_articles)} subsidy articles.")
        
        for article in subsidy_articles:
            try:
                block = article.find_element(By.CLASS_NAME, "article-block")
                
                # Extract information
                title = block.find_element(By.CLASS_NAME, "subsidy-title").text
                
                try:
                    status_elem = block.find_element(By.CLASS_NAME, "subsidy-end-txt")
                    status = status_elem.text
                except NoSuchElementException:
                    status = "公募中"
                    
                try:
                    url_element = block.find_element(By.CLASS_NAME, "subsidy-url")
                    url = url_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                except NoSuchElementException:
                    url = "URL情報なし"
                    
                try:
                    text = block.find_element(By.CLASS_NAME, "subsidy-txt").text
                except NoSuchElementException:
                    text = "説明情報なし"
                
                try:
                    term = block.find_element(By.CLASS_NAME, "subsidy-term").text
                except NoSuchElementException:
                    term = "期間情報なし"
                    
                try:
                    price = block.find_element(By.CLASS_NAME, "subsidy-price").text
                except NoSuchElementException:
                    price = "金額情報なし"

                subsidy_data = {
                    "タイトル": title,
                    "ステータス": status,
                    "URL": url,
                    "説明": text,
                    "期間": term,
                    "金額": price
                }
                
                subsidies.append(subsidy_data)
                print(f"✓ Extracted subsidy: {title}")
                
            except Exception as e:
                print(f"Error extracting subsidy details: {e}")
        
    except TimeoutException:
        print("Timeout waiting for subsidy results to load.")
    except Exception as e:
        print(f"Error in get_subsidy_details: {e}")
    
    return subsidies

def click_checkbox_by_text(driver, text_content):
    """Click a checkbox by finding its label containing the specified text"""
    try:
        xpath = f"//label[contains(., '{text_content}')]"
        label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", label)
        print(f"✓ Successfully clicked checkbox with text: {text_content}")
        return True
    except Exception as e:
        print(f"Error clicking checkbox with text '{text_content}': {e}")
        return False

def process_checkboxes(driver, options, section_name):
    """Process each checkbox option by its text and get the corresponding subsidies"""
    results = []
    
    for option_text in options:
        try:
            print(f"\n==== Processing option: {option_text} ====")
            
            # Make sure we're on the form page
            if "診断結果" in driver.title:
                driver.back()
                time.sleep(3)
            
            # Click the checkbox by its text
            if not click_checkbox_by_text(driver, option_text):
                continue
            
            # Submit the form
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submit01"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", submit_button)
            
            # Wait for results page
            time.sleep(3)
            
            # Check if we're on the results page
            if "診断結果" not in driver.title:
                print("Failed to navigate to results page.")
                continue
            
            # Get subsidies from results page
            subsidies = get_subsidy_details(driver)
            
            # Add section and option information to each subsidy
            for subsidy in subsidies:
                subsidy["セクション"] = section_name
                subsidy["選択した項目"] = option_text
                results.append(subsidy)
            
            # Go back to the form page
            driver.back()
            time.sleep(3)
            
            # Uncheck the checkbox to prepare for next iteration
            if click_checkbox_by_text(driver, option_text):
                print("✓ Unchecked the checkbox")
            
        except Exception as e:
            print(f"Error processing option '{option_text}': {e}")
    
    return results

def save_to_csv(results, filename="subsidy_results.csv"):
    """Save results to CSV without duplicates"""
    # Use a dictionary to track unique entries based on title
    unique_subsidies = {}
    
    for subsidy in results:
        # Create a key from title to identify unique subsidies
        key = subsidy["タイトル"]
        
        if key not in unique_subsidies:
            unique_subsidies[key] = subsidy
        else:
            # If this subsidy already exists, update the record with additional selected options
            existing = unique_subsidies[key]
            if existing["選択した項目"] != subsidy["選択した項目"]:
                existing["選択した項目"] += f", {subsidy['選択した項目']}"
    
    # Convert back to list
    unique_results = list(unique_subsidies.values())
    
    # Define fieldnames for CSV
    fieldnames = ["タイトル", "ステータス", "URL", "説明", "期間", "金額", "セクション", "選択した項目"]
    
    # Write to CSV
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_results)
    
    print(f"✅ CSV出力完了 → {filename}")
    print(f"  合計 {len(unique_results)} 件の補助金情報（重複なし）")

def main():
    driver = setup_driver()
    all_results = []
    
    try:
        # Navigate to the website
        driver.get("https://shindan.jmatch.jp/writeup/?startpacks")
        
        # Initialize form with basic information
        if not initialize_form(driver):
            print("Failed to initialize form. Exiting.")
            return
        
        # Define the sections and their corresponding checkbox text
        sections = {
            "事業成長・改善": [
                "ホームページ制作・ECサイト・採用サイト等（動画含み）・広告出稿を発注したい",
                "新規事業を立ち上げたい（または直近新規事業を開始したばかり）",
                "ITツール・パソコン・タブレットを導入し、社内をDX化したい",
                "システム・ＡＩ開発を発注したい",
                "機械設備・乗用車や内装工事を発注したい",
                "業務用エアコン、照明などを入れ替えたい",
                "買い手もしくは売り手として、事業承継やM＆Aに取り組みたい"
            ],
            "従業員関連": [
                "ＡＩ開発・研修を導入して業務改善に取り組みたい",
                "外部研修を受講してもらい社員にスキルアップを促したい",
                "１年以内に正社員またはアルバイトを１名以上雇用する可能性がある",
                "今後、ご家庭で子供が生まれる可能性がある従業員がいる",
                "アルバイトの待遇改善・給与アップなど行い、できるだけ長く働いてもらいたい",
                "60歳以上の待遇改善・給与アップなど行い、できるだけ長く働いてもらいたい"
            ],
            "業務環境全般": [
                "オンラインでの集客を強化したい",
                "HPを作成したい・新しくしたい",
                "新しい事業を始めようと思っている",
                "オフィスの移転を考えている",
                "税理士とフランクな関係で相談がしたい",
                "事業融資などの資金調達を考えている"
            ]
        }
        
        # Process each section
        for section_name, checkbox_texts in sections.items():
            print(f"\n=== Processing section: {section_name} ===")
            section_results = process_checkboxes(driver, checkbox_texts, section_name)
            all_results.extend(section_results)
        
        # Save all results to CSV
        save_to_csv(all_results)
        
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()