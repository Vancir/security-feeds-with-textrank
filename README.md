# Security Feeds With NLP

## Introduction

Filtering the security news from twitter and recommand what's you may concern.

## Installation

```shell
pipenv shell
pipenv install --dev --pre

# install twint
pip install --upgrade git+https://github.com/twintproject/twint.git@origin/master#egg=twint
twint -u username -o username.json --json

# download en_core_web_sm package
python -m spacy download en_core_web_sm
```

## Quick Start

```shell
python butler.py --help
```