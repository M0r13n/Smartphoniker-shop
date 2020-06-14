from bs4 import BeautifulSoup
from webtest import TestResponse


class TestSitemap:

    def test_sitemap_renders_without_errors(self, db, testapp):
        response = testapp.get("/sitemap.xml")
        assert response.status_code == 200

    def test_robots_txt_exists(self, testapp):
        response = testapp.get("/robots.txt")
        assert response.status_code == 200

    def test_links_in_sitemap_valid(self, db, testapp):
        response: TestResponse = testapp.get("/sitemap.xml")
        soup = BeautifulSoup(response.body)
        tags = soup.find_all("sitemap")
        for sitemap in tags:
            url = sitemap.findNext("loc").text
            r = testapp.get(url)
            assert r.status_code == 200
