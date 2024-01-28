import json
import os
import re
import unicodedata
import time

from configparser import ConfigParser

from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

driver = webdriver.Firefox()
driver.implicitly_wait(1.5)
with open('data.txt', 'r', encoding='utf-8') as fl:
    srcSAT = fl.readlines()
with open('private.txt', 'r', encoding='utf-8') as fl:
    # only the first line is SAT datum
    website = fl.readline()[:-1]
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


def login_webpage():
    driver.get(f"{website}#/login")

    # use cookie to login
    # cookie from EditThisCookie (browser extension) and driver.get_cookie()
    with open('cookie.json', 'r') as cookieF:
        cookie_list = json.load(cookieF)
        for cookie in cookie_list:
            driver.add_cookie(cookie)

    driver.get(website)
    if 'login' in driver.current_url:
        driver.get(website)

    time.sleep(3)
    close_refresh_dialog()


def close_refresh_dialog():
    # detect and confirm refreshment dialog
    try:
        print("closingRefDiag")
        driver.find_element(by=By.XPATH, value='//*[@id="swal2-title"]')
    except common.exceptions.NoSuchElementException:
        print('not found')
    else:
        print("found")
        driver.find_element(by=By.XPATH, value='/html/body/div[3]/div/div[6]/button[1]').click()


def answer(count: int, auto_disabled: bool, default_choice: int, permissive_enabled: bool):
    word_raw = "***"
    try:
        word_raw = driver.find_element(By.XPATH, "//div[@id=\'app\']/div/div[3]/div/div/div[3]/div/div/div/div").text
    except common.exceptions.NoSuchElementException:
        print("\33[7mError! wait for confirm...\33[0m")
        os.system(pausing)
        print(wrong)
    word = str(re.findall(r"(?<=\s)([a-z àâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ-]*)", word_raw)[0])
    word_print = "|" + word + "|"
    print(f"\033[33m{word_print}\033[0m", f"({count})")

    meaning = [
        driver.find_element(By.XPATH, "//div[@id=\'app\']/div/div[3]/div/div/div[3]/div/div[2]/div/label/span").text[3:],
        driver.find_element(By.XPATH, "//div[@id=\'app\']/div/div[3]/div/div/div[3]/div/div[2]/div[2]/label/span").text[3:],
        driver.find_element(By.XPATH, "//div[@id=\'app\']/div/div[3]/div/div/div[3]/div/div[2]/div[3]/label/span").text[3:],
        driver.find_element(By.XPATH, "//div[@id=\'app\']/div/div[3]/div/div/div[3]/div/div[2]/div[4]/label/span").text[3:],
        driver.find_element(By.XPATH, "//div[@id=\'app\']/div/div[3]/div/div/div[3]/div/div[2]/div[5]/label/span").text[3:]]

    tmp = 1
    for m in meaning:
        print("\033[36m" + str(tmp) + ") " + "\033[0m" + str(m))
        tmp += 1

    for line in srcSAT:
        if word_print in line:
            # separate line using |
            result = line.split('|')
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
    ActionChains(driver).send_keys(str(my_choice)).perform()

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
                ActionChains(driver).send_keys(str(my_choice)).perform()
                ActionChains(driver).send_keys(str(choice)).perform()
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
                    ActionChains(driver).send_keys(str(choice)).perform()
                have_partial_answer = True
            if choice == 5 and have_partial_answer:
                # If found, break at last, and unselect the wrong answer (permissive only)
                if permissive_enabled:
                    ActionChains(driver).send_keys(str(my_choice)).perform()
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
    auto_disabled = config.getboolean('SAT', 'DisableAutoMode')
    default_choice = config.getint('SAT', 'defaultChoice')
    permissive_enabled = config.getboolean('SAT', 'permissiveModeEnabled')
    login_webpage()
    print("Login successful")

    while True:
        test_id = config.getint('SAT', 'testID')
        if auto_disabled:
            test_id = input("Which test do you want? Choose order from the top....")
        try:
            driver.find_element(By.XPATH,
                                fr"/html/body/div[1]/div/main/div[7]/div/div[3]/div[5]/div[2]/table/tbody/tr[{test_id}]/td[8]/div/span/button/span").click()
        except common.exceptions.NoSuchElementException:
            os.system(clearScreen)
            print("\33[31mInvalid input.\33[0m\n")
            continue
        try:
            time.sleep(1)
            driver.find_element(By.CSS_SELECTOR, "button.el-button--small:nth-child(1)").click()
        except common.exceptions.NoSuchElementException:
            print("no test style choosing dialog, continue")
        else:
            print("successfully closed the test style choosing dialog")
        try:
            time.sleep(1)
            driver.find_element(By.CSS_SELECTOR, "button.el-button--primary:nth-child(1)").click()
        except common.exceptions.NoSuchElementException:
            print("\33[31mButton cannot be clicked.\33[0m")
            os.system(pausing)
            # goback
            driver.back()
            continue
        else:
            break

    # click startPractice in the practise
    driver.find_element(By.XPATH, "//div[@id=\'app\']/div/div[3]/div/div/div/button/span").click()

    # probe_sum = int(input("total number?...")) + 1
    probe_sum = 100
    for i in range(1, probe_sum + 1):
        answer(i, auto_disabled, default_choice, permissive_enabled)

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
    os.system(pausing)
    print("\n" + "\33[7;36mThe browser is going to quit. Are you sure?\33[0m")
    time.sleep(2)
    os.system(pausing)
    driver.quit()


if __name__ == '__main__':
    main()
