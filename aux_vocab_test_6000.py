import os
import re
import unicodedata
import time

from configparser import ConfigParser

from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.support.relative_locator import locate_with

driver = webdriver.Firefox()
driver.implicitly_wait(1)
with open('6000aux.txt', 'r', encoding='utf-8') as fl:
    src6k = fl.readlines()
wrong = []

system = os.name
if system == "nt":
    clearScreen = "cls"
    pausing = "pause"
elif system == "posix":
    clearScreen = "clear"
    pausing = "bash -c 'read -n 1 -r -p \"Press any key to continue...\" key'"


def normalize_string(s):
    # convert full-width characters to half-width ones
    normalized_s = unicodedata.normalize('NFKC', s)
    # remove non-letters
    cleaned_s = re.sub(r'[^\w\s]', '', normalized_s)
    return cleaned_s

def compare_strings(str1, str2):
    normalized_str1 = normalize_string(str1)
    normalized_str2 = normalize_string(str2)

    return normalized_str1 == normalized_str2


def answer(count: int, auto_disabled: bool, default_choice: int, permissive_enabled: bool):
    div_num = count + 3
    word = "***"
    try:
        word = driver.find_element(By.XPATH, f"/html/body/div[1]/form/div[13]/div[4]/fieldset/div[{div_num}]/div[1]/div").text
    except common.exceptions.NoSuchElementException:
        print("\33[7mError! wait for confirm...\33[0m")
        os.system(pausing)
        print(wrong)
    word_print = "|" + word + "|"
    print(f"\033[33m{word_print}\033[0m", f"({count})")

    meaning = [
        driver.find_element(By.XPATH, f"/html/body/div[1]/form/div[13]/div[4]/fieldset/div[{div_num}]/div[2]/div[1]/div").text,
        driver.find_element(By.XPATH, f"/html/body/div[1]/form/div[13]/div[4]/fieldset/div[{div_num}]/div[2]/div[2]/div").text,
        driver.find_element(By.XPATH, f"/html/body/div[1]/form/div[13]/div[4]/fieldset/div[{div_num}]/div[2]/div[3]/div").text,
        driver.find_element(By.XPATH, f"/html/body/div[1]/form/div[13]/div[4]/fieldset/div[{div_num}]/div[2]/div[4]/div").text]

    tmp = 1
    for m in meaning:
        print("\033[36m" + str(tmp) + ") " + "\033[0m" + str(m))
        tmp += 1

    for line in src6k:
        if word_print in line:
            # separate line using |
            result = line.split('|')
            result[3] = result[3][0:-1]
            print("\n\033[32mSearched result found.\033[0m")
            break
    else:
        print("\n\033[33mNo precise answer found.\033[0m")
        result = "nothing"

    while True:
        my_choice = default_choice
        if auto_disabled:
            my_choice = input("Now choose your answer.....")
        try:
            my_choice = int(my_choice)
        except:
            continue
        else:
            if my_choice < 1 or my_choice > 5:
                continue
            else:
                break
    driver.find_element(By.CSS_SELECTOR, f"#div{div_num} .ui-radio:nth-child({str(my_choice)}) .jqradio").click()

    print("\nResult searched is ", "|", result[3])
    for m in meaning:
        if compare_strings(result[3], m):
            choice = meaning.index(m) + 1
            print("The correct choice is ", choice)
            if my_choice == choice:
                print("\033[32mTrue\033[0m\n")
            else:
                print("\033[31mFalse\033[0m")
                wrong.append(word)
                driver.find_element(By.CSS_SELECTOR, f"#div{div_num} .ui-radio:nth-child({choice}) .jqradio").click()
                print("\033[36mCorrect answer has been chosen.\033[0m")
                if auto_disabled:
                    time.sleep(1)
            break
    else:
        print("\033[31mNo precise choice.\033[0m")
        result_n = normalize_string(result[3])
        have_partial_answer = False
        choice = 1
        for m in meaning:
            m_n = normalize_string(m)
            if m_n in result_n or result_n in m_n:
                print("\033[33mPartial answer found:\033[0m" + m)
                if permissive_enabled:
                    choice = meaning.index(m) + 1
                    # Select partial choices
                    driver.find_element(By.CSS_SELECTOR, f"#div{div_num} .ui-radio:nth-child({choice}) .jqradio").click()
                have_partial_answer = True
            if choice == 5 and have_partial_answer:
                # If found, break at last, and unselect the wrong answer (permissive only)
                if permissive_enabled:
                    driver.find_element(By.CSS_SELECTOR, f"#div{div_num} .ui-radio:nth-child({my_choice}) .jqradio").click()
                break
        else:
            print("\033[7mResult is ", result[3], "\033[0m", "\n\033[7mNo choice meets.\033[0m")
        if auto_disabled or not permissive_enabled:
            print("Now choose by yourself.")
            os.system(pausing)

    if auto_disabled:
        os.system(pausing)
    os.system(clearScreen)


def main():
    if system == "nt":
        os.system("chcp 65001")
    # read config from config.ini
    config = ConfigParser()
    config.read('config.ini', encoding='UTF-8')
    auto_disabled = config.getboolean('6000', 'DisableAutoMode')
    default_choice = config.getint('6000', 'defaultChoice')
    permissive_enabled = config.getboolean('6000', 'permissiveModeEnabled')
    print("Initializing...")
    with open("TestList.txt", encoding='utf-8') as f:
        tl = f.readlines()
    with open('private.txt', 'r', encoding='utf-8') as f:
        private_data = f.readlines()
        # private_data[0] is SAT datum, skipping
        stu_id = private_data[1][:-1]
        stu_name = private_data[2][:-1]
        if clearScreen == 'cls':
            dest = private_data[3][:-1]
        else:
            dest = private_data[4][:-1]
        stu_class = private_data[5]

    while True:
        test_id = config.getint('6000', 'testID')
        if auto_disabled:
            test_id = input("Which test do you want? From 1 to 31....")
        try:
            test_url = str(tl[int(test_id) - 1].split("\t")[1])[0:-1]
            driver.get(test_url)
        except common.exceptions.NoSuchElementException:
            os.system(clearScreen)
            print("\33[31mInvalid input.\33[0m\n")
            continue
        try:
            # try to find the first word and test if the webpage is successfully loaded
            driver.find_element(By.XPATH, "/html/body/div[1]/form/div[13]/div[4]/fieldset/div[4]/div[1]/div").click()
        except common.exceptions.NoSuchElementException:
            print("\33[31mThe webpage is broken.\33[0m")
            os.system(pausing)
            # goback
            driver.back()
            continue
        else:
            break

    print("\nNow filling necessary info...")
    driver.find_element(By.XPATH, "//span[text()='请选择']").click()
    driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input').send_keys(stu_class)
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    my_id = locate_with(By.TAG_NAME, "input").below({By.XPATH: "//div[text()='学号：']"})
    driver.find_element(my_id).send_keys(stu_id)
    my_name = locate_with(By.TAG_NAME, "input").below({By.XPATH: "//div[text()='您的姓名：']"})
    driver.find_element(my_name).send_keys(stu_name)
    print("\nComplete!")
    time.sleep(0.5)
    os.system(clearScreen)

    for i in range(1, 41):
        answer(i, auto_disabled, default_choice, permissive_enabled)

    driver.find_element(By.XPATH, '//*[@id="ctlNext"]').click()  # submit the test


    print("-------------------------------------------------")
    if len(wrong) != 0:
        w_num = 0
        for word in wrong:
            w_num += 1
            print(w_num, ".", "\033[33m", word, "\033[0m")
        print("\ntotal: ", "\033[31m", w_num, "\033[0m")
    else:
        print("\33[32mAll done! 100% Correct!\33[0m")
    print("-------------------------------------------------")
    print("Saving Screenshots...wait for 3 seconds")
    try:
        time.sleep(3)
        driver.save_screenshot(fr"{dest}\{test_id}.png")
    except:
        print("\033[1;4;31;40mCouldn't capture the screenshot, DO IT BY YOURSELF!!!\033[0m")
    else:
        print("\033[1;4;34;40mScreenshot has been saved!\033[0m")
    print("-------------------------------------------------")
    os.system(pausing)
    print("\n" + "\33[7;36mThe browser is going to quit. Are you sure?\33[0m")
    time.sleep(2)
    os.system(pausing)
    driver.quit()


if __name__ == '__main__':
    main()
