# notebooks
List of notebooks for users

## Instructions ##
After bringing the entire project to your computer, create a conda environment (named **notebook_environment** here)
```
conda create -n notebook_environment python=3.6
```

Activate the environment
```
conda activate notebook_environment
```

Then run the following script to install all the necessary libraries
```
./.script_for_installation.sh
```

## for developpers ##

Before pushing any changes you made, clean up the notebook by running the command
```
 $ python before_and_after_github_script.py -b
```

and before pushing to repository
```  
$ python before_and_after_github_script.py -a
```

This will reset all the notebooks (clear output) and will allow github to clearly see the differences between notebooks
that have been modified.

To turn debugging mode on, add the flag -d (--use_debugging_mode) to the command

```
$ python before_and_after_github_script.py -a -d
```
