"""
A module for parsing files
"""

import pandas as pd
import os
from .util import Util
import sys


class Parse:
    """
    A class to house the parsing logic

    Attributes
    ----------
    util : Util class
        a set of utility functions from the Util class
    symbs : list[str]
        a list of symbols that denote version numbers in a requirements.txt
    """
    def __init__(self):
        self.util = Util()
        self.symbs = ["==", ">", ">=", "<", "<=", "~=", "~", "@"]

    @staticmethod
    def read_file(proj, file_name):
        """
        Looks for files in the django parent directory.
        If file not found the script exits the run time and tells you
            - where the script looked for the file
            - what command to run to generate the file if it's not there.
            - asks you to move it to the correct directory if it exists

        :param proj: (str) The django project parent directory
            Example: ~/django
        :param file_name: (str) The file being read
            One of treefreeze.txt or requirements.txt
        :return: (pd.Series) a pandas Series of the lines of the file read.
        """
        path = os.path.join(proj, file_name)
        try:
            with open(path, 'r') as file:
                lines = pd.Series([line for line in file])
            return lines
        except FileNotFoundError:
            print("I could not find the file " + file_name + ",")
            print("In the path " + path)
            if file_name == 'treefreeze.txt':
                cmd = 'pipdeptree -f > treefreeze.txt'
            else:
                cmd = 'pip freeze > requirements.txt'
            print("Please run '" + cmd + "' in your django project directory.")
            print("If this file already exists please move me to the above location.")
            sys.exit()

    def requirements(self, proj):
        """
        Reads the requirements.txt to create a pandas dataframe to parse import statements
        TODO: Make this work for installs from git
        :param proj: (str) The django project parent directory
            Example: ~/django
        :return: (pd.Series) a pandas Series of the pkgs from the requirements.txt.
        """
        reqs = self.read_file(proj, 'requirements.txt')  # reads the file is a pd.Series
        # [
        # pandas==1.3.4,
        # numpy>1.20,
        # scipy~=1.7.1
        # ]
        pkg_names = reqs.apply(lambda requirement: self.util.find_requirements_name(requirement, self.symbs))  # parses the file
        pkg_names = pkg_names.rename('pkg')  # sets the series names
        # [
        # pandas,
        # numpy,
        # scipy
        # ]
        return pkg_names

    def treefreeze(self, proj):
        """
        Reads the treefreeze.txt to create a pandas dataframe to parse import statements
        :param proj: (str) The django project parent directory
            Example: ~/django
        :return: (pd.Series) a pandas Series of the pkgs from the treefreeze.txt.
        """
        reqs = self.requirements(proj)  # parses the requirements.txt for names
        tree_file = self.read_file(proj, 'treefreeze.txt')  # pd.Series of the treefreeze.txt
        # [
        #  pandas @ file:///C:/ci/pandas_1635506685681/work,
        #   numpy @ file:///C:/ci/numpy_and_numpy_base_1626271900803/work,
        #   python-dateutil @ file:///tmp/build/80754af9/python-dateutil_1626374649649/work,
        #       six @ file:///tmp/build/80754af9/six_1623709665295/work,
        #   pytz==2021.3
        # ]
        pkg_names = tree_file.apply(lambda requirement: self.util.find_requirements_name(requirement, self.symbs))  # parses the requirements.txt for names
        # [
        #  pandas
        #   numpy,
        #   python-dateutil,
        #       six,
        #   pytz
        # ]
        pkg_names = pkg_names.rename('pkg')  # sets series name
        # pipdeptree does not include pkgs without dependencies
        # find these within the requirements.txt
        not_in_tree_file = reqs[~reqs.isin(pkg_names)]
        # add them to the tree output
        pkg_names = pkg_names.append(not_in_tree_file)
        # this is a list of either
        # requirements with don't have a leading tab
        # or a dependency which do have a leading tab
        req_dep = self.util.iter_packages(pkg_names)
        # creates the base for requirements.csv
        # starts as 0 and becomes 1 when we encounter the import later
        req_dep['used'] = 0
        print(req_dep)
        return req_dep
