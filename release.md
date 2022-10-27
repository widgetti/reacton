
# fully automated

    $ ./release.sh 0.14.0

# semi automated
To make a new release
```
# update reacton/_version.py
$ git add -u && git commit -m 'Release v0.14.0' && git tag v0.14.0 && git push upstream master v0.14.0
```


If a problem happens, and you want to keep the history clean
```
# do fix
$ git rebase -i HEAD~3
$ git tag v0.14.0 -f &&  git push upstream master v0.14.0 -f
```
