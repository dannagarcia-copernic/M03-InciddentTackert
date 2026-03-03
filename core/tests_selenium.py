import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

class SecurityRegressionTests(StaticLiveServerTestCase):
    fixtures = ['testdb.json'] # Càrrega de dades

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless") # Mode Headless per al servidor

        # Rutes intel·ligents
        snap_bin = "/snap/firefox/current/usr/lib/firefox/firefox"
        linux_bin = "/usr/bin/firefox"

        if os.path.exists(snap_bin):
            opts.binary_location = snap_bin
        elif os.path.exists(linux_bin):
            opts.binary_location = linux_bin

        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'selenium'):
            cls.selenium.quit()
        super().tearDownClass()

    def test_role_restriction(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        self.selenium.find_element(By.NAME, "username").send_keys("analista1")
        self.selenium.find_element(By.NAME, "password").send_keys("supersecret") # La teva clau
        self.selenium.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        self.assertNotEqual(self.selenium.title, "Site administration | Django site admin")
