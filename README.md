# notebooks
List of notebooks for users

## Instructions ##

To recover notebook, runs following commands

```
 $ python before_and_after_github_script.py -b
```

and before pushing to repository

```  
$ python before_and_after_github_script.py -a
```

This will reset all the notebooks (clear output)

To turn debugging mode on, add the flag -d (--use_debugging_mode) to the command

```
$ python before_and_after_github_script.py -a -d
```
