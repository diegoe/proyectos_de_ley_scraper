# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import log

from pdl_scraper.items import PdlPdfUrlItem
from pdl_scraper.models import db_connect


class PdfUrlSpider(scrapy.Spider):
    name = "pdfurl"
    allowed_domains = ["www2.congreso.gob.pe"]

    def __init__(self, category=None, *args, **kwargs):
        super(PdfUrlSpider, self).__init__(*args, **kwargs)
        self.start_urls = self.get_my_urls()

    def parse(self, response):
        res = re.search("\/([0-9]{5})\?", response.url)
        if res:
            codigo = res.groups()[0]
            item = PdlPdfUrlItem()
            item['pdf_url'] = self.find_pdfurl(codigo, response)
            item['codigo'] = codigo
            yield item

    def find_pdfurl(self, codigo, response):
        for sel in response.xpath("//a"):
            href = sel.xpath("@href").extract()[0]

            pattern = re.compile("\$FILE\/" + str(codigo) + "\.pdf$")
            if re.search(pattern, href):
                log.msg("Found pdfurl for code: %s" % str(codigo))
                return href

            pattern = re.compile("\$FILE\/.*" + str(codigo) + "[0-9]+\.*-?\.pdf$")
            if re.search(pattern, href):
                log.msg("Found pdfurl for code: %s" % str(codigo))
                return href

            pattern = re.compile("\$FILE\/.+" + str(codigo) + "[0-9]+\.PDF$")
            if re.search(pattern, href):
                log.msg("Found pdfurl for code: %s" % str(codigo))
                return href

        log.msg("We failed to parse pdfurl for this project %s:" % str(codigo))
        return ''

    def get_my_urls(self):
        """
        Find those proyectos with no PDF url in our database.
        :return: set of URLs
        """
        db = db_connect()
        start_urls = []
        append = start_urls.append

        # get list of proyects ids from pdl_proyecto table with no events
        query = "select expediente, pdf_url from pdl_proyecto"
        res = db.query(query)
        for i in res:
            if i['pdf_url'] is None or i['pdf_url'].strip() == '':
                append(i['expediente'])
                log.msg('Appending %s to start_urls.' % str(i['expediente']))

        return start_urls
