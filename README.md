<h1>Check files for unused imports and unused packages in requirements.txt</h1>
<h3>Has been optimized for speed</h3>

<h3>Steps</h3>
<ol>
    <li>cd /Users/yashbehal/projects/doorstep-django</li>
    <li>Run 'pipdeptree -f > treefreeze.txt'
        <ul>
            <li>If I don't work run 'pip install pipdeptree' and run again</li>
            <li>If I don't work again run 'python /root/.cache/activestate/868be8dc/lib/python2.7/site-packages/pipdeptree.py -f > /root/django/treefreeze.txt'</li>
            <li>Change /root/.cache/activestate/868be8dc/lib/python2.7/site-packages/ to be your site package location</li>
            <li>Change /root/django/ to be your django root project directory</li>
        </ul>
    </li>
    <li>Remove what we just did
        <ol>
            <li>rm -rf pylinttest</li>
            <li>rm -rf lint_dir</li>
        </ol>
    </li>
    <li>Clone me into the dd repository
        <ul>
            <li>git clone https://github.com/travistheall/lint_dir</li>
        </ul>
    </li>
    <li>See image for python script set up</li>
    <li>Hit play</li>
    <li> Current Errors to expect:
        <ul>
            <li>Error Requirement backoff not found in /root/.cache/activestate/868be8dc/lib/python2.7/site-packages</li>
            <li>Error Dependency subprocess32 of matplotlib not found in /root/.cache/activestate/868be8dc/lib/python2.7/site-packages</li>
            <li>Error Requirement pkgconfig not found in /root/.cache/activestate/868be8dc/lib/python2.7/site-packages</li>
            <li>Error Requirement poetry-core not found in /root/.cache/activestate/868be8dc/lib/python2.7/site-packages</li>
            <li>Error Requirement Python not found in /root/.cache/activestate/868be8dc/lib/python2.7/site-packages</li>
        </ul>
    </li>
    <li>Creates 2 files
        <ol>
            <li>not_in_requirements.csv: A csv file with all the packages that are used in the project, but not in requirements.txt</li>
            <ul>
                <li>math, os, project modules, ...</li>
            </ul>
            <li>requirements.csv: A csv file with all the packages from requirements.txt and 1 if used 0 if not</li>
        </ol>
    </li>
    <li>Run me Monday morning. Let me know how this goes. It's sunday and I'm tired of working.</li>
</ol>

<h2>Pycharm Config To Run Script</h2>
<h4>Configure a python3 interpreter</h4>
<img src="https://user-images.githubusercontent.com/58260017/148442415-b7cb3297-4c36-4027-85df-53a3439ea147.png" />
