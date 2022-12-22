
# fully automated

    $ ./release.sh 0.17.2

# semi automated
To make a new release
```
# update reacton/_version.py
$ git add -u && git commit -m 'Release v0.17.2' && git tag v0.17.2 && git push upstream master v0.17.2
```


If a problem happens, and you want to keep the history clean
```
# do fix
$ git rebase -i HEAD~3
$ git tag v0.17.2 -f &&  git push upstream master v0.17.2 -f
```
