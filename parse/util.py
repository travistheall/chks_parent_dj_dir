"""
A module for the utility functions needed for parsing files
"""

import site
import os
import pandas as pd


def find_my_site_packages():
    """
    Static function to find your site package directory.
    !# may need to change me depending on the environment
    :return: (str) directory location of this python environment's site packages
    """
    print('You may need to change me depending on your environment')
    pkgs_dir = site.getsitepackages()[1]
    # [
    #   ' /root/.cache/activestate/868be8dc/lib/python2.7/site-packages/',
    #   '/root/.cache/activestate/868be8dc/lib/site-python'
    # ]
    # pkgs_dir = '/root/.cache/activestate/868be8dc/lib/python2.7/site-packages'
    # pkgs_dir = '/opt/ActivePython-2.7/lib/python2.7/site-packages'
    print('I should be something similar to /root/.cache/activestate/868be8dc/lib/python2.7/site-packages')
    print(pkgs_dir)
    return pkgs_dir


class Util:
    """
    A class to house the utility functions needed for parsing files

    Attributes
    ----------
    site_pkgs_dir : str
        a directory path to check the site-packages
    """
    def __init__(self):
        self.site_pkgs_dir = find_my_site_packages()

    @staticmethod
    def find_requirements_name(requirement_line, search_list):
        """
        finds the package name without version number
        :params requirement_line: (str) single line read from requirements.txt or treefreeze.txt
        :params search_list: (List[str]) a list of strings to search for within in the line.

        example 1 requirement.txt:
        requirement_line  | loc (symbol location)
        _____________________________________________
        matplotlib~=3.4.3 | 10
        numpy>1.20        | 5
        pandas            | 0

        :returns cleaned name
            matplotlib
            numpy
            pandas

        example 2 treefreeze.txt:
        requirement_line                | loc (symbol location)
        _____________________________________________
        zope.event-4.5.0-py3.9.egg-info | 16
        xlrd-2.0.1.dist-info            | 10
        xlwt                            | 0

        :returns cleaned names
            zope.event-4.5.0
            xlrd-2.0.1.dist-info
            xlwt
        """
        symb = [requirement_line.find(search) for search in search_list if search in requirement_line]
        if len(symb) > 0:
            # this finds requirements with versions
            # matplotlib~=3.4.3 finds "~=" at position 10
            # returns matplotlib
            loc = symb[0]
            return requirement_line[:loc]
        else:
            # this finds requirements with no versions
            # returns matplotlib
            return requirement_line

    def iter_packages(self, pkg_names):
        """
        :param pkg_names: a pd series with requirements and their dependencies

        amazon-dax-client==1.1.8
          antlr4-python2-runtime==4.7.2
          botocore==1.20.112
            jmespath==0.10.0
            python-dateutil==2.8.2
              six==1.16.0
            urllib3==1.26.4
          futures==3.3.0
          six==1.16.0
        amazon-dax-client is the requirements
        everything indented under it is the dependencies of the above req

        :return: a pd dataframe with the requirement and it's dependencies
        """
        import_names = self.get_import_names()
        req_dep = pd.DataFrame(columns=['pkg', 'dep'])
        req = ''
        for index, req_or_dep in pkg_names.iteritems():
            req_or_dep = req_or_dep.rstrip()
            if req_or_dep.startswith('  '):
                # then it's a dependency
                dep = req_or_dep
                # remove indents
                dep = dep.lstrip()
                try:
                    dep = import_names.loc[dep]['import_name']
                    l_req_dep = pd.DataFrame(data=[[req, dep]], columns=['pkg', 'dep'])
                    req_dep = req_dep.append(l_req_dep)
                    # sets index for faster look ups
                    req_dep.set_index('pkg', inplace=True)
                    return req_dep
                except KeyError:
                    print('Error Dependency ' + dep + ' of ' + req + ' not  found in ' + self.site_pkgs_dir)
            else:
                # then it's a requirement
                req = req_or_dep
                try:
                    req = import_names.loc[req]['import_name']
                    l_req_dep = pd.DataFrame(data=[[req, req]], columns=['pkg', 'dep'])
                    req_dep = req_dep.append(l_req_dep)
                    # sets index for faster look ups
                    req_dep.set_index('pkg', inplace=True)
                    return req_dep
                except KeyError:
                    print('Error Requirement ' + req + ' not found in ' + self.site_pkgs_dir)

    def get_top_level_txt(self, pkg_dir_name):
        """
        :param pkg_dir_name: (str)
        :return: (str)
            either the import name from the top_lvl.txt or the directory name
        """
        fname = "top_level.txt"
        if os.path.isdir(pkg_dir_name):
            for pkg_contents in os.listdir(pkg_dir_name):
                if pkg_contents == fname:
                    top_level_file_path = os.path.join(self.site_pkgs_dir, fname)
                    # PIL, cryptography, etc
                    with open(top_level_file_path, "r") as top_level_file:
                        lines = [line for line in top_level_file]
                    top_lvl_name = lines[0].strip()
                    return top_lvl_name

        return pkg_dir_name

    def get_import_names(self):
        """
        function to find the import names from the environment's site packages
        Example:
        requirement name: Pillow (pip install Pillow)
        import name: PIL (import PIL)
        :return: pandas dataframe with the requirement name and the import name
        """
        pkg_dir_names = pd.Series(os.listdir(self.site_pkgs_dir), name="dir_name")
        top_lvl_names = pkg_dir_names.apply(lambda dir_name: self.get_top_level_txt(dir_name))

        top_lvl_names.rename("top_lvl_name", inplace=True)
        top_lvl_names = pd.concat([pkg_dir_names, top_lvl_names], axis=1)
        endings = [
            ".post1-py2.7.egg-info",
            "-py3.6.egg-info",
            "-py3.7-nspkg.pth",
            "-py3.9-win-amd64.egg-info",
            ".cp39-win_amd64.pyd",
            ".dist-info",
            ".dist-info'",
            "-py2.7.egg-info",
            "-py3.9.egg-info",
            "-py3.9.egg",
            "-py3.9-nspkg.pth",
            ".py",
            "-py3.10.egg-info"
        ]
        reqs = top_lvl_names['dir_name'].apply(lambda name: self.find_requirements_name(name, endings))
        # string parsing
        # changes XlsxWriter-3.0.1 into XlsxWriter==3.0.1
        reqs = reqs.str.replace('-', "==")
        reqs = reqs.str.replace('_', "-")
        reqs.rename('requirement', inplace=True)
        import_names = pd.concat([top_lvl_names['dir_name'], top_lvl_names['top_lvl_name'], reqs], axis=1)
        requirements = import_names[import_names['requirement'].str.contains('==')]
        requirements[['import_name', 'req_version']] = requirements['requirement'].str.split('==', expand=True)
        requirements = requirements[['requirement', 'import_name']]
        # req_name | import_name
        # --------------------------
        # Pillow     |  PIL
        # cryptography| cryptography
        requirements.set_index('import_name', inplace=True, drop=True)
        return requirements
