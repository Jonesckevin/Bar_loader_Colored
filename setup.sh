## Check and install pip
if ! command -v pip &> /dev/null
then
    echo "pip could not be found, installing..."
    sudo apt-get install python3-pip -y
else
    echo "pip is already installed"
fi

## Check, Install and Create a virtual environment
if ! command -v virtualenv &> /dev/null
then
    echo "virtualenv could not be found, installing..."
    sudo apt-get install python3-venv -y
else
    echo "virtualenv is already installed"
fi
python3 -m venv venv

source venv/bin/activate

## Check and install requirements
if ! [ -f requirements.txt ]; then
    echo "requirements.txt not found, please check the directory"
    exit 1
fi
## Install requirements
pip install -r requirements.txt

