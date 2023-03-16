
# fully automated

    $ ./release.sh 1.3.4

# semi automated
To make a new release
```
# update reacton/_version.py
$ git add -u && git commit -m 'Release v1.3.4' && git tag v1.3.4 && git push upstream master v1.3.4
```


If a problem happens, and you want to keep the history clean
```
# do fix
$ git rebase -i HEAD~3
$ git tag v1.3.4 -f &&  git push upstream master v1.3.4 -f
```
