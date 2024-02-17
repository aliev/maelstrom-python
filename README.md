# Maelstrom Python Implementation

This repository is an attempt at an asynchronous implementation of a [Maelstrom](https://github.com/jepsen-io/maelstrom) node in Python. While there are existing [Python](https://github.com/jepsen-io/maelstrom/tree/main/demo/python) implementations, this project distinguishes itself through true asynchronous communication with stdin/stdout/stderr. Additionally, it represents my endeavor to work through all chapters of the Maelstrom documentation.

## Installation

To begin, you must first install Maelstrom.

Maelstrom is developed in Clojure, requiring the installation of OpenJDK:

```bash
brew install openjdk graphviz gnuplot
```

Once your environment is ready for Maelstrom, proceed to install Maelstrom itself.

Navigate to [this link](https://github.com/jepsen-io/maelstrom/releases/tag/v0.2.3), download, and unpack the release. Verify that you can run it by executing:

```bash
./maelstrom serve
```

The next step is to obtain the absolute path to the unpacked Maelstrom directory. Execute `pwd`, copy the output path, and clone this repository into your desired directory:

```bash
git clone git@github.com:aliev/maelstrom-python.git
cd maelstrom-python
```

Create a virtual environment within the repository directory, ensuring you are using Python version 3.11 or higher:

```bash
python -m venv .venv
```

Install the development dependencies:

```bash
make dev-install
```

Next, create a `.env` file and specify the absolute path to the Maelstrom directory:

```bash
echo "MAELSTROM_BIN_PATH=/path/to/maelstrom" > .env
```

You are now set to run tests:

For echo:

```bash
make test-echo
```

For broadcast:

```bash
make test-broadcast
```

To run a Maelstrom node:

```bash
mnode
```
