import scrapy

from find_doctor.person import CreateObject


class DoctorSpider(scrapy.Spider):
    name = "doctor"
    allowed_domains = ["www.regiongavleborg.se/", "http://ltblekinge.se/, http://www.ltdalarna.se/"]
    start_urls = [
        "http://www.regiongavleborg.se/A-O/Vardgivarportalen/Lakemedel/Lakemedelskommitten/Organisation/Lakemedelskommittens-terapigrupper/",
        "http://www.regiongavleborg.se/A-O/Vardgivarportalen/Lakemedel/Lakemedelskommitten/Organisation/Lakemedelskommittens-ledamoter/",
        "http://ltblekinge.se/For-vardgivare/Lakemedel/Lakemedelskommitten/Organisation/",
        "http://www.ltdalarna.se/For-vardpersonal/For-vardpersonal/Lakemedel-i-Dalarna/Dalarnas-lakemedelskommitte/Ledamoter/"
    ]

    def parse(self, response):
        date = response.xpath("//p[@id='pageinfo']/text()|"
                              "//div[@id='footerinfoarea']/text()|"
                              "//div[@class ='infoarticle']/p/text()").re('\d{1,4}-\d{1,2}-\d{1,2}') or ['']
        rows = response.xpath("//div[@class='mainbody editor']/ul/li|"
                              "//div[@class='mainbody editor']/p|"
                              "//div[@class='maincontent']/div/table[@class='linjeradOrange']/tbody/tr|"
                              "//div[@class='editorcontent']/div//p")
        for row in rows:
            person_in_list = row.xpath(".//text()").extract()
            if 'Vakant' not in person_in_list:
                email = row.xpath("./a/@href").re('[a-zA-Z0-9._]+\@[a-zA-Z0-9._]+\.[a-zA-Z]{2,}') or []
                person_in_list += email
                person = CreateObject(person_in_list, date[0], response.url)
                yield person.get_fields()