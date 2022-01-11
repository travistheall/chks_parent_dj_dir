import pandas as pd
import os
from .util import Util
import sys


class Parse:
    def __init__(self):
        self.util = Util()
        self.symbs = ["==", ">", ">=", "<", "<=", "~=", "~", "@"]

    @staticmethod
    def read_file(proj, file_name):
        """
        Looks for files in the django parent directory. If file not found rells you where it looked
        and what command to run to generate the file.
        :param proj: The django project parent directory
        :param file_name: The file being read
        :return: a pandas Series of the lines of the file read.
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
        Reads the requiremetns.txt to create a pandas dataframe to parse pylint results
        """
        reqs = self.read_file(proj, 'requirements.txt')
        pkg_names = reqs.apply(lambda requirement: self.util.find_requirements_name(requirement, self.symbs))
        pkg_names = pkg_names.rename('pkg')
        return pkg_names

    def treefreeze(self, proj):
        """
        Reads the treefreeze.txt to create a pandas dataframe to parse pylint results
        """
        reqs = self.requirements(proj)
        tree_file = self.read_file(proj, 'treefreeze.txt')
        pkg_names = tree_file.apply(lambda requirement: self.util.find_requirements_name(requirement, self.symbs))
        pkg_names = pkg_names.rename('pkg')

        not_in_tree_file = reqs[~reqs.isin(pkg_names)]
        pkg_names = pkg_names.append(not_in_tree_file)
        req_dep = self.util.iter_packages(pkg_names)
        # creates the base for requirements.csv
        # starts as 0 and becomes 1 when we encounter the import later
        req_dep['used'] = 0
        return req_dep
