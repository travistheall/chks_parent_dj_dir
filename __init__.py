"""
Module to parse requirements for used and unused packages.
"""
import os
import time
from datetime import datetime
import pandas as pd
from parse import Parse


class CheckParentDjangoDirectory:
    """
    Class used to parse if requirements are used in a project.
    Steps:
        1. Then checks IMPORT statements of files in modules
        2. Then updates whether a requirement was used
        3. Exports to a csv (requirements.csv)
            a. 0 = not used
            b. 1 = used
        4. If an import is used but not in requirements.txt
            it is added to not_in_requirements.txt
            1 column.
            All packages in the file are used.

    Attributes
    ----------
        now : (str) timestamp
        chks_parent_dj_dir : (str) the directory this code lives in
        parent_dj_proj : (str) the directory of the django project
        parse : (Parse) a parsing class (parse/__init__.py)
        req : (pd.DataFrame) [cols: []]
        not_in_req : (pd.DataFrame) [cols: []]
    """

    def __init__(self, chks_parent_dj_dir):
        self.now = str(time.mktime(datetime.now().timetuple()))[:-2]
        self.chks_parent_dj_dir = chks_parent_dj_dir
        self.parent_dj_proj = os.path.dirname(chks_parent_dj_dir)
        self.parse = Parse()
        self.req = self.parse.treefreeze(self.parent_dj_proj)
        self.not_in_req = pd.Series(name='pkg')

    def parse_project_file(self, imports):
        """
        Checks each individual file for the used and unused packages
        Changes used from 0 to 1 if used.
        If it is used once then we should not remove it once iteration is over

        :param imports: (pd.Series) lines with the import statements
        """
        # removes excess words only keep package name
        # from numpy import add => ["from", "numpy", "import", "add"]
        # import numpy as np => ["import", "numpy", "as", "np"]
        # from django.db import blah => ["from", "django.db", "import", "blah"]
        # from .lint import Lint => ["from", ".lint", "import", "Lint"]
        pkgs = imports.str.split(" ", expand=True)[1]
        # numpy
        # django.db
        # .lint
        pkgs = pkgs.str.split('.', expand=True)[0]
        # django.db => django
        # .lint => ""
        # .lint would cause an error because nothing there
        # this gets rid of those blank imports
        pkgs = pkgs[pkgs != ""]
        pkgs.reset_index(drop=True)
        req_pkgs = pkgs[pkgs.isin(self.req.index)]
        if req_pkgs.any():
            # where this index matches in the requirements df increment + 1
            r = self.req.loc[req_pkgs]
            print(r)
            self.req.at[req_pkgs, 'used'] = 1
        else:
            # ~ is a bitwise not in python means not in requirements below
            not_req_pkgs = pkgs[~pkgs.isin(self.req.index)]
            not_req_pkgs = not_req_pkgs.rename('pkg')
            # if there is nothing then it just appends nothing so nothing happens
            self.not_in_req = self.not_in_req.append(not_req_pkgs, ignore_index=True)
            # make a huge series. we'll drop duplicates at the end b4 exporting

    def loop_dir(self, directory):
        """
        Recursively look through directories
        This fn pretty pointless I just thought
        there was too much indentation

        :param directory: directory name
        """
        for file_or_dir in os.listdir(directory):
            self.route_file_dir(directory, file_or_dir)

    def check_if_empty_file(self, f_name):
        """
        completely empty files returns an error
        This checks for the empty files or empty imports before parsing

        continues on to parse_project_file if not empty
        ends search if empty

        :param  f_name: (str) filename
        """
        with open(f_name, 'r') as file:
            lines = pd.Series([line for line in file])
        # checks for any empty files to avoid crashing
        if lines.any():
            lines = lines.str.strip()
            # import statement starts with import
            i_import = lines[lines.str.startswith('import')]
            # import statement starts with from
            f_import = lines[lines.str.startswith('from')]
            # all import statments
            a_imports = i_import.append(f_import)
            # checks for any blank imports
            # no lines that start with import or from
            if a_imports.any():
                self.parse_project_file(a_imports)

    def route_file_dir(self, parent_dir, file_or_dir):
        """
        :param file_or_dir: file or directory name
        :param parent_dir: parent directory name
        """
        # full file path
        parent_w_child = os.path.join(parent_dir, file_or_dir)
        if len(file_or_dir.split(".")) == 1:  # if it's a directory
            # 'proj'.split(".") => ['proj'] => len == 1
            self.loop_dir(parent_w_child)
        elif file_or_dir.split(".")[1] == 'py':  # it's a py file
            # 'parse.py'.split(".") => ['Check', 'py'] => len == 2
            self.check_if_empty_file(parent_w_child)
        else:  # it's a reg  file
            pass

    def export(self):
        """
        Creates two files
        requirements-now.csv:
            contains all the packages from the requirements and 0 if not used 1 if used
        not_in_requirements-now.csv:
            IMPORT statements that were not declared in requirement.txt but were used
        """
        req_csv = os.path.join(self.chks_parent_dj_dir, 'requirements-' + self.now + '.csv')
        print('exporting to ' + req_csv)
        self.req.sort_values(by=['used'], inplace=True, ascending=False)
        self.req.drop_duplicates(keep='first', inplace=True)
        self.req.to_csv(req_csv)
        not_req_csv = os.path.join(self.chks_parent_dj_dir, 'not_in_requirements-' + self.now + '.csv')
        self.not_in_req.drop_duplicates(keep='first', inplace=True)
        print('exporting to ' + not_req_csv)
        self.not_in_req.to_csv(not_req_csv, index=False, header=True)

    def run(self):
        """
        Main function to run program
        Loops through all the directories
        """
        print('checking for unused requirements')
        parent_dj_proj_files = [x for x in os.listdir(self.parent_dj_proj) if x not in ['chks_parent_dj_dir']]
        for file_or_dir in parent_dj_proj_files:
            self.route_file_dir(self.parent_dj_proj, file_or_dir)

        self.export()
        print('parse done')
