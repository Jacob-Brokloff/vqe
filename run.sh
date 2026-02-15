#!/bin/bash

# Setup venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Setting up environment..."
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install qiskit qiskit-aer qiskit-ibm-runtime scipy matplotlib
else
    source .venv/bin/activate
fi

python main.py
