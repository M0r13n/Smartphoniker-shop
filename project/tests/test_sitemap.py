from bs4 import BeautifulSoup
from webtest import TestResponse

from project.server.models import Manufacturer


class TestSitemap:

    def test_sitemap_renders_without_errors(self, db, testapp):
        response = testapp.get("/sitemap.xml").follow()
        assert response.status_code == 200

    def test_robots_txt_exists(self, testapp):
        response = testapp.get("/robots.txt").follow()
        assert response.status_code == 200

    def test_links_in_sitemap_valid(self, db, testapp):
        response: TestResponse = testapp.get("/sitemap.xml").follow()
        soup = BeautifulSoup(response.body)
        tags = soup.find_all("url")
        Manufacturer.create(name="Apple")
        Manufacturer.create(name="Samsung")
        Manufacturer.create(name="Huawei")
        for sitemap in tags:
            url = sitemap.findNext("loc").text
            r = testapp.get(url).follow()
            assert r.status_code == 200
