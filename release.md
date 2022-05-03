
# fully automated

    $ ./release.sh 0.6.0

# semi automated
To make a new release
```
# update react-ipywidgets/_version.py
$ git add -u && git commit -m 'Release v0.6.0' && git tag v0.6.0 && git push upstream master v0.6.0
```


If a problem happens, and you want to keep the history clean
```
# do fix
$ git rebase -i HEAD~3
$ git tag v0.6.0 -f &&  git push upstream master v0.6.0 -f
```
