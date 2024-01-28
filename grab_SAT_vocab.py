import json
import os
import time
from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, Keys
import re

driver = webdriver.Firefox()
driver.implicitly_wait(1.5)

with open('private.txt', 'r', encoding='utf-8') as fl:
    # only the first line is SAT datum
    website = fl.readline()[:-1]

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


def fetch_content(click_span_xpath_number):
    # fetch text procedure
    span_xpath = fr'/html/body/div[1]/div/div[2]/div[1]/div/div[2]/div/div/div[{str(click_span_xpath_number)}]/a/span'
    driver.find_element(by=By.XPATH, value=span_xpath).click()
    click_span = driver.find_element(by=By.XPATH, value=span_xpath).text
    word_end_count = int(re.findall(r"\d+$", click_span)[0])  # define last word's No.
    # time.sleep(0.3)


    # # just scroll to bottom using keyboard down arrow
    # for i in range(1, 31):
    #     ActionChains(driver) \
    #         .send_keys(Keys.ARROW_DOWN) \
    #         .perform()


    # define view_all switch (div, role='switch')
    switch_view_all = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div/div")
    # get sensitive attr
    aria_checked = switch_view_all.get_attribute("aria-checked")
    # if closed, open it (click span(acts like a btn))
    if aria_checked != "true":
        time.sleep(2)
        driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div/div/span").click()

    # now fetch texts
    while True:
        # fetch raw
        wod = driver.find_element(by=By.XPATH,
                                  value="/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div/span").text
        chn = driver.find_element(by=By.XPATH,
                                  value="/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div/div/div[2]").text
        eng = driver.find_element(by=By.XPATH,
                                  value="/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div/div/div[3]").text
        wodattr = driver.find_element(by=By.XPATH,
                                      value="/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div/div/div[1]").text
        # filter them to get what we want
        word_serial = int(re.findall(r"\d+", wod)[0])
        word_content = str(re.findall(r"(?<=\.\s)([a-z àâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ-]*)", wod)[0])
        try:
            word_attr = str(re.findall(r"(?<=\s)([a-z]+\.?)(?=\s)", wodattr)[0])
        except IndexError:
            print("Word ", word_serial, "has wrong attribute, rollback to raw content")
            word_attr = wodattr

        '''
        chn_content = str(re.findall(r"(?<=^(.{4})).*", chn)[0])
        '''
        chn_content = chn[4:]
        eng_content = eng[4:]

        final = str(word_serial) + "|" + word_content + "|" + word_attr + "|" + chn_content + "|" + eng_content
        print(final)
        with open('data.txt', 'a+', encoding='utf-8') as f:
            f.write(final)
            f.write("\n")

        if word_serial == word_end_count:
            print("done")
            break
        else:
            # time.sleep(0.01)
            # goto next one
            ActionChains(driver) \
                .send_keys(Keys.ARROW_RIGHT) \
                .perform()


def main():
    if os.name == "nt":
        os.system("chcp 65001")
    login_webpage()
    # define pos for 词汇下拉按钮
    vocab_div_hover = driver.find_element(by=By.XPATH, value="/html/body/div[1]/section/div/ul/li[2]/div")
    ActionChains(driver) \
        .move_to_element(vocab_div_hover) \
        .perform()  # hover it
    time.sleep(1)
    driver.find_element(by=By.XPATH, value='/html/body/div[4]/ul/li[4]').click()  # click 词表学习
    # define pos for "chrome brwsr offi down"
    home_div_hover = driver.find_element(by=By.XPATH, value="/html/body/div[1]/section/div/ul/li[5]")
    ActionChains(driver) \
        .move_to_element(home_div_hover) \
        .perform()  # hover it
    time.sleep(0.5)
    # click 请选择词表
    driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/div/div[1]/div/div/div/input').click()
    print("星期三")
    time.sleep(0.5)
    # click SAT重点词汇 (span)
    driver.find_element(by=By.XPATH, value='/html/body/div[6]/div[1]/div[1]/ul/li').click()
    time.sleep(0.5)

    # fetch text procedure
    for i in range(1, 86):
        print("\nnow in number", i, "span\n")
        fetch_content(i)
        # time.sleep(0.3)

    print("Completed!")

    driver.quit()


if __name__ == '__main__':
    main()
