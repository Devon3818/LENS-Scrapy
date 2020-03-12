from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger
import time

class SeleniumMiddleware():
  def __init__(self, timeout=None):
    self.logger = getLogger(__name__)
    self.timeout = timeout

    self.browser = webdriver.Firefox()
    self.browser.set_page_load_timeout(self.timeout)
    self.wait = WebDriverWait(self.browser, self.timeout)

  def __del__(self):
    self.browser.close()

  def process_request(self, request, spider):

    province = int(request.meta['province']) - 1
    city = int(request.meta['city']) - 1
    district = int(request.meta['district']) - 1
    dtime = int(request.meta['dtime'])

    try:
      self.browser.get(request.url)
      try:
        close_element = WebDriverWait(self.browser, 10).until(
          EC.presence_of_element_located((By.CLASS_NAME, "sufei-dialog-close"))
        )
        close_element.click()
      except TimeoutException:
        return HtmlResponse(url=request.url, status=500, request=request)

      self.browser.find_element_by_class_name('ph-appoint').click()
      self.browser.find_element_by_class_name('store-text').click()
      time.sleep(dtime)
      self.browser.find_elements_by_xpath('//li[@class = "city-select-item"]')[0].click()
      time.sleep(dtime)
      self.browser.find_elements_by_xpath('//div[@class = "select-menu-wrapper show"]//div[@class = "select-menu-item"]')[province].click()
      time.sleep(dtime)
      self.browser.find_elements_by_class_name('city-select-item')[1].click()
      time.sleep(dtime)
      self.browser.find_elements_by_xpath('//div[@class = "select-menu-wrapper show"]//div[@class = "select-menu-item"]')[city].click()
      time.sleep(dtime)
      self.browser.find_elements_by_class_name('city-select-item')[2].click()
      time.sleep(dtime)
      self.browser.find_elements_by_xpath('//div[@class = "select-menu-wrapper show"]//div[@class = "select-menu-item"]')[district].click()
      time.sleep(dtime)
      return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8', status=200)

    except TimeoutException:
      return HtmlResponse(url=request.url, status=500, request=request)

  @classmethod
  def from_crawler(cls, crawler):
    s = cls(timeout=40)
    return s