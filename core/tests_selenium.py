import os
import shutil
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
        opts.add_argument("--headless") # Requisit: mode Headless

        # RUTA PARA UBUNTU SNAP (Ya funciona)
        snap_bin = "/snap/firefox/current/usr/lib/firefox/firefox"
        if os.path.exists(snap_bin):
            opts.binary_location = snap_bin
        else:
            opts.binary_location = "/usr/bin/firefox"

        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(10) # Espera a que carguen los elementos

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'selenium'):
            cls.selenium.quit()
        super().tearDownClass()

    def test_role_restriction(self):
        """AUDITORIA: L'analista no ha d'entrar a /admin/"""
        # 1. Vamos a la URL de login del ADMIN (es la más común en esta práctica)
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))

        # 2. Login con 'analista1'
        # Buscamos los campos 'username' y 'password'
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")

        username_input.send_keys("analista1")
        password_input.send_keys("supersecret") # Tu contraseña de la P3

        # Hacemos clic en el botón de login (en Django Admin es un input de tipo submit)
        self.selenium.find_element(By.XPATH, '//input[@type="submit"]').click()

        # 3. Intentamos forzar la URL del panel principal
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))

        # 4. ASSERT de Seguridad: Comprobamos si el título es el de administración
        # Fase RED: El analista ENTRA, por lo que el título será igual y el test FALLARÁ.
        self.assertNotEqual(self.selenium.title, "Site administration | Django site admin")
