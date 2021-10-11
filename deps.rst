dev container setup cheat sheet
-------------------------------

.. code::

    locale-gen
    add-apt-repository ppa:deadsnakes/ppa

    apt update
    apt install tox bzr build-essential twine python-all python-all-dev python3-all python3-all-dev python3-docutils python3-sphinx python3-flake8 python-flake8 python2.4-complete python2.5-complete python2.6-complete python3.1-complete python3.2-complete python3.3-complete python3.4-complete python3.5 python3.5-dev python3.7 python3.7-dev  python-wheel python3-wheel python-pip python3-pip


    wget https://raw.githubusercontent.com/pypa/setuptools/bootstrap-py24/ez_setup.py -O - | python2.4
    wget https://raw.githubusercontent.com/pypa/setuptools/bootstrap-py24/ez_setup.py -O - | python2.5
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python2.6
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python3.1
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python3.2
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python3.3
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python3.4
