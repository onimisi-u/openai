Install python:
```
export PATH="/usr/local/opt/python/libexec/bin:$PATH"
brew install python
```

Create a new environment with Streamlit
```
python -m venv .venv
pip install streamlit
```

Install openAi
```
pip install openai
```

Use your new environment
Any time you want to use the new environment, you first need to go to your project folder (where the .venv directory lives) and run:
```
source .venv/bin/activate
```
Now you can use Python and Streamlit as usual:
```
streamlit run myfile.py
```

To stop the Streamlit server, press `ctrl-C`.

When you're done using this environment, type `deactivate` to return to your normal shell.