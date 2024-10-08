https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/win64/chrome-headless-shell-win64.zip
https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/win64/chromedriver-win64.zip
https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/linux64/chromedriver-linux64.zip
https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.86/linux64/chrome-headless-shell-linux64.zip
https://googlechromelabs.github.io/chrome-for-testing/#beta
https://www.chromedriverdownload.com/en/downloads/chromedriver-128-download


iptables -A INPUT -s 10.0.0.4 -p tcp --destination-port 27017 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -d 10.0.0.4 -p tcp --source-port 27017 -m state --state ESTABLISHED -j ACCEPT

~/projects/work/buybot/chrome/128/chromedriver-linux64/chromedriver
~/projects/work/buybot/chrome/128/chrome-headless-shell-linux64/chrome-headless-shell