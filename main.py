from __init__ import CheckParentDjangoDirectory
import os


# cd /Users/yashbehal/projects/doorstep-django
# git clone https://github.com/travistheall/chks_parent_dj_dir

# PYCHARM SETTINGS CONFIG FILE SCRIPT PATH:
#       /Users/yashbehal/projects/doorstep-django/chks_parent_dj_dir/main.py
# PYCHARM SETTINGS CONFIG FILE PYTHON INTERPRETER:
#       python3 env with pandas
# IN A TERMINAL RUN:
#       pip3 install -r requirements.txt
#       from config working directory
# PYCHARM SETTINGS CONFIG FILE WORKING DIR:
#       /Users/yashbehal/projects/doorstep-django/chks_parent_dj_dir/

# PYCHARM SETTINGS CONFIG FILE OPTIONAL:
# OPEN EXCECUTION IN PYCHARM SETTINGS:
#       CHECK "Run with Python console."
#       This allows you to more easily debug.
#       see img.png for a picture of my config


# FILES OUTPUT DIR:
#   /Users/yashbehal/projects/doorstep-django/chks_parent_dj_dir/
# FILES:
#       not_in_requirements-timestamp.csv
#       requirements-timestamp.csv


if __name__ == '__main__':
    print('You are running me from the working directory of ' + os.getcwd())
    print("If your django project direcotry is ~/django,")
    print("You should be running me from the ~/django/chks_parent_dj_dir.")
    print("I am expecting there to be a ~/django/requirements.txt & a ~/django/treeparse.txt")
    check = CheckParentDjangoDirectory(chks_parent_dj_dir=os.getcwd())
    check.run()
    print('program finished')
