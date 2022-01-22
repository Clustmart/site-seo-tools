# site-seo-tools

## Table of Contents 

- [Installation](#installation)
- [Creating a Shell Script](#creating-a-shell-script)
- [Cronjob](#cronjob)

---

## Installation

You want to work with venv, so in the project folder create your venv folder and activate the python environment (so all dependencies you install )
'''shell
python3 -m venv env
source env/bin/activate
'''

Install dependencies: robobrowser, xlrd  and pandas

```shell
pip install robobrowser
pip install pandas
```
**If you have a werkzeug Error Read this** As of February 2020 `werkzug` upgraded to 1.0.0 and RoboBrowser lazy developers havent fixed. To fix this you need to go to your Robobrowser folder on your computer something like (/Users/yourusername/opt/anaconda3/lib/python3.7/site-packages/robobrowser/) and open `browser.py` and add change ```from werkzeug import cached_property  ``` to ```from werkzeug.utils import cached_property```
Please take a look at this url for more info: [Link to issue](https://github.com/jmcarp/robobrowser/issues/93)
