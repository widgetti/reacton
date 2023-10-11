
# fully automated

    $ ./release.sh 1.7.2

# semi automated
To make a new release
```
# update reacton/_version.py
$ git add -u && git commit -m 'Release v1.7.2' && git tag v1.7.2 && git push upstream master v1.7.2
```


If a problem happens, and you want to keep the history clean
```
# do fix
$ git rebase -i HEAD~3
$ git tag v1.7.2 -f &&  git push upstream master v1.7.2 -f
```
