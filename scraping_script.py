# Script that will scrape the descriptions of the jobs offered by some of the most
# important companies in the IT sector
# The name of those companies will be stored in a list, on 'constants.py'

# This script only takes care of scraping the descriptions and saving all the descriptions into a
# In order to scrape it I will combine unigrams (word counts) and n-grams, particularly bigrams (n=2)

# Actions chains are a way to automate low level interactions such as
# mouse movements, mouse button actions, key press. It generate user actions


import csv
import pickle
import sys
import time

import regex
import spacy
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import constants as const

# Load English model
nlp = spacy.load("en_core_web_sm")

config = dotenv_values(".env")


class Linkedin(webdriver.Chrome):

    def __init__(self, companies):
        options = webdriver.ChromeOptions()
        options.add_argument("--force-device-scale-factor=0.2")
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # Initialize parent class
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.name_company_according_to_linkedin = ""
        self.enterprise_job = ""
        self.title_job = ""
        self.description_job = ""
        self.companies = companies
        self.progress_companies = 0
        self.number_jobs = 0

    def get_data(self):
        self.__land_first_page()
        self.__sign_in()
        self.__search_title()
        self.__search_location()
        # Loop over companies that I pass as an argument when instantiating the class
        for company in self.companies:
            # Print progress
            print(
                f"##### {round(self.progress_companies/len(self.companies)*100)}% completed #####"
            )

            self.__search_company(company)
            # self.__load_whole_page()
            # Find all jobs in first page for given company
            jobs = self.__get_company_jobs()
            self.number_jobs = len(jobs)
            # Loop over all the jobs that a company has on the first page
            for i, job in enumerate(jobs, 1):
                print(f"\t{i}/{self.number_jobs} jobs scraped")
                # Select job
                self.__select_job(job)
                # Get info about the job
                self.__extract_info_job()
                clean_description_job = self.__process_description_job()

                # Append job description into a txt
                with open("description_jobs.txt", "a", encoding="utf-8") as f:
                    f.write(clean_description_job + "\n")
                time.sleep(2)
            self.number_jobs = 0
            self.progress_companies += 1
            time.sleep(2)
            # Reset company filter, so we get a clean slate for next company
            self.__reset()

        return None

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
        search_btn = self.find_element(
            By.XPATH,
            "//div[@id='global-nav-search']//button[contains(@class,'jobs-search-box__submit-button')]",
        )
        search_btn.click()

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

        self.name_company_according_to_linkedin = self.find_element(
            By.XPATH,
            "//div[@id='hoverable-outlet-company-filter-value']//input[@aria-label='Add a company']",
        ).get_attribute("value")

        # Check company search has worked
        if not self.name_company_according_to_linkedin.upper() == company.upper():
            sys.exit()
        else:
            print(
                f"{self.name_company_according_to_linkedin.upper()} is equal to {company.upper()}"
            )

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
        # At first it returned me the info of random jobs, because it needs some time
        # to load all the jobs of the company of interest
        WebDriverWait(self, 30).until(
            EC.text_to_be_present_in_element(
                (
                    By.XPATH,
                    "//div[contains(@class,'job-details-jobs-unified-top-card__company-name')]/a",
                ),
                self.name_company_according_to_linkedin,
            )
        )

    def __get_company_jobs(self):
        jobs = self.find_elements(
            By.XPATH,
            "//main[@id='main']//div[@class='scaffold-layout__list ']//ul[li/div/div[@data-job-id]]/li",
        )
        return jobs

    def __extract_info_job(self):
        description_job = self.find_element(
            By.XPATH,
            "//div[@id='job-details']",
        )
        description_job = description_job.get_attribute("outerHTML")

        self.description_job = description_job

    def __select_job(self, job):
        job.click()

    def __process_description_job(self):
        clean_description = self.strip_html_tags(self.description_job)
        return clean_description

    def __reset(self):
        reset_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Reset applied filters']"
        )
        reset_btn.click()

    # Method to remove the html tags from the jobs description
    @staticmethod
    def strip_html_tags(text):
        html_tags = regex.compile("<.*?>", flags=regex.DOTALL)
        partially_clean = regex.sub(html_tags, " ", text)
        double_spaces = regex.compile(r"\s+")
        clean = regex.sub(double_spaces, " ", partially_clean)
        return clean


item = Linkedin(const.ENTERPRISES)
item.get_data()
