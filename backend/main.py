import csv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time

# ドライバ起動（必要に応じてパス指定）
driver = webdriver.Chrome()

# 対象のURLにアクセスして、基本情報入力
driver.get("https://shindan.jmatch.jp/writeup/?startpacks")
time.sleep(5)  
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "MAIL[q2]")))
Select(driver.find_element(By.NAME, "MAIL[q2]")).select_by_visible_text("1-5名")
Select(driver.find_element(By.NAME, "MAIL[q27]")).select_by_visible_text("建設業")
driver.find_element(By.ID, "all-1").click()

# # 「事業」
checkbox_ids = [16, 10, 11, 12, 17, 18, 19]


for q in checkbox_ids:
    try:
        # チェックボックス全解除
        for prev_q in checkbox_ids:
            try:
                checkbox = driver.find_element(By.NAME, f"MAIL[q{prev_q}]")
                if checkbox.is_selected():
                    driver.execute_script("arguments[0].checked = false;", checkbox)
            except:
                pass

        # チェック対象ラベルを探す
        try:
            label = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f"//label[input[@name='MAIL[q{q}]']]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", label)
            label.click()
        except:
            print(f"MAIL[q{q}] のラベルが見つかりませんでした。スキップします。")
            continue

        # 診断ボタン押下
        driver.find_element(By.ID, "submit01").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "article-block")))

        block = driver.find_element(By.CLASS_NAME, "article-block")
        title = block.find_element(By.CLASS_NAME, "subsidy-title").text

        try:
            status = block.find_element(By.CLASS_NAME, "subsidy-end-txt").text
        except:
            status = "公募中"

        url = block.find_element(By.CLASS_NAME, "subsidy-url").text
        text = block.find_element(By.CLASS_NAME, "subsidy-txt").text
        term = block.find_element(By.CLASS_NAME, "subsidy-term").text
        price = block.find_element(By.CLASS_NAME, "subsidy-price").text

        print(f"\n==== MAIL[q{q}] ====")
        print("タイトル:", title)
        print("ステータス:", status)
        print("URL:", url)
        print("説明:", text)
        print("期間:", term)
        print("金額:", price)

        # 一覧に戻る
        driver.back()
        time.sleep(2)

    except Exception as e:
        print(f"MAIL[q{q}] でエラー: {e}")


# === CSV出力 ===
with open("subsidy_results.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["MAIL項目", "タイトル", "ステータス", "URL", "説明", "期間", "金額"])
    writer.writeheader()
    writer.writerows(results)

print("✅ CSV出力完了 → subsidy_results.csv")


# ブラウザを閉じる
driver.quit()

