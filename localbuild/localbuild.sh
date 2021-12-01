
# If there's no lock file, build one
# Then pop up a level and install sdg as a local, editable module
# Then install whatevers missing the nasty way
FILE=./Pipfile.lock
if [ ! -f "$FILE" ]; then
    pipenv install
    cd .. && pipenv run Python3 setup.py install && cd localbuild

    # Badly setup yaml module
    pipenv install git+https://github.com/dougmet/yamlmd#egg=yamlmd
    
    # TODO - at the moment the pypi for csvcubed is bugged, work around, but check this every so often
    pip install "git+https://github.com/GSS-Cogs/csvcubed.git#egg=csvcubed-models&subdirectory=csvcubed-models"
    pip install "git+https://github.com/GSS-Cogs/csvcubed.git#egg=csvcubed&subdirectory=csvcubed"
    pip install "git+https://github.com/robons/pydantic.git@72a15dccae95cc9680e207d5fcac000586162837#egg=pydantic"
fi

rm -rf ./localbuild/_site
pipenv run python3 localbuild.py