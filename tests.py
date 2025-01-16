import unittest
from generate_site import generate_html_jinja


class TestUtils(unittest.TestCase): ...


class Testdb(unittest.TestCase): ...


class TestAi(unittest.TestCase): ...


class TestSiteGenerator(unittest.TestCase):
    def test_generate_html_jinja(self):
        html = generate_html_jinja({}, output_dir="/tmp")
        print(html)


if __name__ == "__main__":
    unittest.main()
