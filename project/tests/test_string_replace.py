from project.server.common.escape import cleanify


class TestReplacements:

    def test_ae(self):
        assert cleanify("") == ""
        assert cleanify("Äpfel") == "Aepfel"
        assert cleanify("äpfel") == "aepfel"
        assert cleanify("Äpfel Äpfel äpfel") == "Aepfel Aepfel aepfel"

    def test_oe(self):
        assert cleanify("Ömel") == "Oemel"
        assert cleanify("ömel") == "oemel"
        assert cleanify("Ömel ömel Ömel") == "Oemel oemel Oemel"

    def test_ue(self):
        assert cleanify("Ümel") == "Uemel"
        assert cleanify("ümel") == "uemel"
        assert cleanify("Ümel ümel Ümel") == "Uemel uemel Uemel"

    def test_ss(self):
        assert cleanify("Scheiße") == "Scheisse"
