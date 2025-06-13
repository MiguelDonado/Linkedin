# Script that will scrape the requirements of the jobs offered by some of the most
# important companies in the IT sector
# The name of those companies will be stored in a list, on 'constants.py'
# In order to scrape it I will combine unigrams (word counts) and n-grams, particularly bigrams (n=2)

# Actions chains are a way to automate low level interactions such as
# mouse movements, mouse button actions, key press. It generate user actions


import csv
import time

import regex
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import constants as const

config = dotenv_values(".env")
# print(config["MY_SECRET_KEY"])


class Linkedin(webdriver.Chrome):

    def __init__(
        self,
    ):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # Initialize parent class
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()

    def get_data(self):
        self.__land_first_page()
        self.__sign_in()
        self.__search_title()
        self.__search_location()
        self.__search_company("NVIDIA")

        # # Get urls of all jobs
        # jobs_urls = self.__extract_jobs_urls()
        # counter = 1
        # education_words = {}
        # essential_words = {}
        # additional_words = {}

        # for job_url in jobs_urls:
        #     self.__land_job_page(job_url)
        #     requirements = self.__extract_requirements_job()
        #     # print(requirements)

        #     # Get education paragraph
        #     education = regex.search(const.EDUCATION_PATTERN, requirements)
        #     if education:
        #         education = education.group(1) or ""
        #         education = regex.sub(r"\n+", " ", education)
        #     else:
        #         education = ""
        #     education_job_words = BSC.count_words(education)
        #     education_words = BSC.sum_dicts(education_words, education_job_words)
        #     # print(education_words)

        #     # Get essential knowledge paragraph
        #     essential = regex.search(const.ESSENTIAL_PATTERN, requirements)
        #     if essential:
        #         essential = essential.group(2) or ""
        #         essential = regex.sub(r"\n+", " ", essential)
        #     else:
        #         essential = ""
        #     essential_job_words = BSC.count_words(essential)
        #     essential_words = BSC.sum_dicts(essential_words, essential_job_words)
        #     # print(essential_words)

        #     # Get additional knowledge
        #     additional = regex.search(const.ADDITIONAL_PATTERN, requirements)
        #     if additional:
        #         additional = additional.group(2) or ""
        #         additional = regex.sub(r"\n+", " ", additional)
        #     else:
        #         additional = ""
        #     additional_job_words = BSC.count_words(additional)
        #     additional_words = BSC.sum_dicts(additional_words, additional_job_words)
        #     # print(additional_words)
        #     # print(counter)

        #     # counter += 1
        #     # if counter == 5:
        #     #     break

        # all_sections = BSC.sum_dicts(education_words, essential_words)
        # all_sections = BSC.sum_dicts(all_sections, additional_words)
        # # all_sections = dict(
        # #     sorted(all_sections.items(), key=lambda item: item[1], reverse=True)
        # # )
        # noun_counts = {
        #     word: count for word, count in all_sections.items() if BSC.is_noun(word)
        # }
        # noun_counts = dict(
        #     sorted(noun_counts.items(), key=lambda item: item[1], reverse=True)
        # )

        # with open("BSC-CNS.csv", "w", newline="") as csvfile:
        #     writer = csv.writer(csvfile)

        #     writer.writerow(["word", "count"])

        #     for word, count in noun_counts.items():
        #         writer.writerow([word, count])

        # return None

    #
    #
    #
    #
    #
    #
    #
    ################################### PRIVATE METHODS ############################################
    #
    #
    #
    #
    #
    #
    #

    # Lands on an Ine webpage
    def __land_first_page(self):
        self.get(const.JOBS_URL)

    def __sign_in(self):
        accept_cookies_btn = self.find_element(
            By.XPATH, '//button[@action-type="ACCEPT"]'
        )
        accept_cookies_btn.click()

        account_input = self.find_element(By.XPATH, "//input[@id='session_key']")
        account_input.send_keys(config["MY_SECRET_ACCOUNT"])

        password_input = self.find_element(By.XPATH, "//input[@id='session_password']")
        password_input.send_keys(config["MY_SECRET_PASSWORD"])

        sign_in_button = self.find_element(
            By.XPATH, "//button[@data-id='sign-in-form__submit-btn']"
        )
        sign_in_button.click()

    def __search_title(self):
        title_input = self.find_element(
            By.XPATH, "//input[contains(@id, 'jobs-search-box-keyword-id')]"
        )
        title_input.send_keys(const.TITLE)
        title_input.send_keys(Keys.ENTER)

    def __search_location(self):
        location_input = self.find_element(
            By.XPATH, "//input[contains(@id, 'jobs-search-box-location-id')]"
        )
        location_input.clear()
        location_input.send_keys(const.LOCATION)
        location_input.send_keys(Keys.ESCAPE)

    def __search_company(self, company):
        time.sleep(2)
        company_button = self.find_element(
            By.XPATH, "//button[@id='searchFilter_company']"
        )
        company_button.click()

        company_input = self.find_element(
            By.XPATH,
            "//div[@id='hoverable-outlet-company-filter-value']//input[@aria-label='Add a company']",
        )
        company_input.send_keys(company)

        time.sleep(2)

        xpath_expression = (
            f"//div[contains(@id, 'basic-result')]//span/span[text()='{company}']"
        )

        first_result = self.find_element(By.XPATH, xpath_expression)
        first_result.click()

        search_btn = self.find_element(
            By.XPATH,
            "//div[@id='hoverable-outlet-company-filter-value']//button[@aria-label='Apply current filter to show results']",
        )
        search_btn.click()

        search_update_worldwide_btn = self.find_element(
            By.XPATH,
            "//div[@id='global-nav-search']//button[contains(@class,'jobs-search-box__submit-button')]",
        )
        search_update_worldwide_btn.click()

        # dropdown_companies = self.find_element(
        #     By.XPATH,
        #     "//div[contains(@id, 'triggered-expanded')]",
        # )
        # print(dropdown_companies.get_attribute("outerHTML"))

    # def __extract_jobs_urls(self):
    #     jobs_urls = self.find_elements(
    #         By.XPATH, "//div[@id='main']//div[@class='view-content']/ul/li//a"
    #     )
    #     jobs_urls = [job_url.get_attribute("href") for job_url in jobs_urls]
    #     return jobs_urls

    # def __land_job_page(self, job_url):
    #     self.get(job_url)

    # # Let the instance on the webpage that shows data about the ref
    # def __extract_requirements_job(self):
    #     requirements = self.find_element(
    #         By.XPATH, "//div[b[text()='Requirements']]/following-sibling::ul"
    #     )
    #     return requirements.text

    # # In order to count the words, I saw I could have used regex to split the words into a list,
    # # And collection.Counter to count the words in the list
    # # But I felt like doing it from scratch, just to play a little bit with the logic (loops, conditionals...)
    # @staticmethod
    # def count_words(text):
    #     # 1. Split the text into words
    #     allowed_symbols = ["_", "-"]
    #     # List that will hold all words
    #     words = []
    #     # Variable that will hold a word
    #     word = ""
    #     for char in text:
    #         if char.isalnum() or char in allowed_symbols:
    #             word += char.lower()
    #         else:
    #             if word != "":
    #                 words.append(word)
    #                 word = ""
    #     # 2. Handle last word
    #     if word != "":
    #         words.append(word)

    #     # Count ocurrences
    #     word_count = {}
    #     for w in words:
    #         if w in word_count:
    #             word_count[w] += 1
    #         else:
    #             word_count[w] = 1
    #     return word_count

    # @staticmethod
    # def sum_dicts(d1, d2):
    #     result = {}

    #     # Add all items from d1
    #     for key in d1:
    #         result[key] = d1[key]

    #     # Add items from d2
    #     for key in d2:
    #         if key in result:
    #             result[key] += d2[key]
    #         else:
    #             result[key] = d2[key]

    #     return result

    # @staticmethod
    # # Check if a word is a noun
    # def is_noun(word):
    #     doc = nlp(word)
    #     for token in doc:
    #         if token.pos_ in ("NOUN", "PROPN"):
    #             return True
    #         return False


item = Linkedin()
item.get_data()
