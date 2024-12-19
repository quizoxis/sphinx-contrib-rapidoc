=======
rapidoc
=======


Local Development Environment Setup
------------------------------------

- To setup local test/debug environment us the following comands:

.. code-block:: bash
   :linenos:

   mkdir sphinxcontrib-rapidoc-hostproject
   cd sphinxcontrib-rapidoc-hostproject

   python -m venv .venv
   source .venv/bin/activate
   pip install sphinx
   sphinx-quickstart --quiet --sep --project="RapiDocHost Sphinx Project" --author="QO" -v "1.0" --release="1.0.1b" --language="en"

   git clone git@github.com:quizoxis/sphinx-contrib-rapidoc.git rapidoc

   # Install test requirements
   pip install -r ./rapidoc/test-requirements.txt

   # Install rapidoc in editable mode
   pip install -e ./rapidoc

   # Copy sample conf.py to source directory
   cp rapidoc/docs/conf.py source

   # Copy sample specs to source directory
   cp -r rapidoc/docs/_specs source

   # Run sphinx build command
   make clean && make html

