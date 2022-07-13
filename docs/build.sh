echo `pwd`
ls -lR .
cd docs
jupyter lite build --config jupyterlite_config.json --contents ../notebooks
ls -lR .
