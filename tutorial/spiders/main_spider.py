import scrapy
from selenium import webdriver
import time
import json
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class MainSpider(scrapy.Spider):
  name = 'main'
  isAgain = 1
  _province = -1
  _city = -1
  _district = -1

  _province_now = 1
  _city_now = 1
  _district_now = 1

  _type = 3
  
  def __init__(self, dtime=3):
    self.dtime = dtime

  def start_requests(self):
    req = scrapy.Request(url = 'https://detail.tmall.com/item.htm?spm=a1z10.3-b-s.w4011-15914629068.72.3652202115XZpy&id=564678780779&rn=1eb2c950c226a70815f00218b1a7a4c0&abbucket=5&skuId=3737918466332&time=' + str( int(time.time()) ), callback = self.parse)
    req.meta['province'] = self._province_now
    req.meta['city'] = self._city_now
    req.meta['district'] = self._district_now
    req.meta['dtime'] = self.dtime
    yield req

  def parse(self, response):

    _list = response.css('.store-item')
    _sele_city = response.css('.city-select-item::text').extract()
    _pname = _sele_city[0]
    _cname = _sele_city[1]
    _dname = _sele_city[2]

    if self.isAgain == 1:
      self.isAgain = 2
      _sele_menu = response.css('.select-menu-wrapper')

      if len(_sele_menu) > 0:
        for _index in range(len(_sele_menu)):

          if _index == 0:
            if self._province_now == 1:
              self._province = len(_sele_menu[ _index ].css('.select-menu-item'))
              print '_province:' + str(self._province)

          if _index == 1:
            self._city = len(_sele_menu[ _index ].css('.select-menu-item'))
            print '_city:' + str(self._city)

          if _index == 2:
            self._district = len(_sele_menu[ _index ].css('.select-menu-item'))
            print '_district:' + str(self._district)

    if len(_list) > 0:
      for _index_al in range(len(_list)):

        _name = _list[ _index_al ].css('.name::text').extract_first()
        _address = _list[ _index_al ].css('.store-address::text').extract_first()
        _phone = _list[ _index_al ].css('.store-info p::text').extract()[2]

        with open('data.html', 'a+') as f:

          _data = [{
            "province": _pname,
            "city": _cname,
            "district": _dname,
            "store": _name,
            "address": _address,
            "phone": _phone
          }]

          f.write(json.dumps(_data, ensure_ascii=False))
          f.write('\n')

    req = scrapy.Request(url = 'https://detail.tmall.com/item.htm?spm=a1z10.3-b-s.w4011-15914629068.72.3652202115XZpy&id=564678780779&rn=1eb2c950c226a70815f00218b1a7a4c0&abbucket=5&skuId=3737918466332&time=' + str( int(time.time()) ), callback = self.parse)
    req.meta['dtime'] = self.dtime

    if self._type == 3:
      if self._district_now != self._district:
        req.meta['province'] = self._province_now
        req.meta['city'] = self._city_now
        self._district_now = int(self._district_now) + 1
        req.meta['district'] = self._district_now
      else:
        self._district_now = 1
        self._type = 2


    if self._type == 2:
      if self._city_now != self._city:
        req.meta['province'] = self._province_now
        self._city_now = int(self._city_now) + 1
        req.meta['city'] = self._city_now
        req.meta['district'] = self._district_now
      else:
        self._city_now = 1
        self._type = 1

    if self._type == 1:
      if self._province_now != self._province:
        self._province_now = int(self._province_now) + 1
        req.meta['province'] = self._province_now
        req.meta['city'] = 1
        req.meta['district'] = 1

        self._city_now = 1
        self._district_now = 1

        self.isAgain = 1
        self._type = 3
      else:
        print 'over!!'
        return

    yield req