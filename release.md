
# fully automated

    $ ./release.sh patch

# semi automated
To make a new release
```
# update reacton/_version.py
$ git add -u && git commit -m 'Release v1.10.3' && git tag v1.10.3 && git push upstream master v1.10.3
```


If a problem happens, and you want to keep the history clean
```
# do fix
$ git rebase -i HEAD~3
$ git tag v1.10.3 -f &&  git push upstream master v1.10.3 -f
```
