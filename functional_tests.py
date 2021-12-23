from selenium import webdriver

# browser = webdriver.Firefox(executable_path=r'your\path\geckodriver.exe')
browser = webdriver.Firefox()
browser.get('http://localhost:8000')

assert 'Congratulations!' in browser.title
