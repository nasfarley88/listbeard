from subprocess import check_call
from skybeard.utils import setup_beard

# Y'all will need the spacy data. This will download the data if it is not
# present, and print a harmless warning message if it is.
check_call("python -m spacy.en.download", shell=True)

setup_beard("listbeard")
