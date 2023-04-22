So I installed miniconda with python3.7 on 1 March 2023. Reason: GoldenCheetah
requires Python 3.7 and I did not want some system wide installation. Also did
not want to pollute my shell or anything, so did not run `conda init`. By not
doing so, it told me the following:


> You have chosen to not have conda modify your shell scripts at all.
> To activate conda's base environment in your current shell session:
> 
> ```
> eval "$(/opt/miniconda3.7-gc/bin/conda shell.YOUR_SHELL_NAME hook)"
> ```
> 
> To install conda's shell functions for easier access, first activate,
> then:
> 
> ```
> conda init
> ```
> 
> If you'd prefer that conda's base environment not be activated on
> startup, set the auto_activate_base parameter to false:
> 
> ```
> conda config --set auto_activate_base false
> ```
> 
> Thank you for installing Miniconda3!

## Further Setup

Some stuff is needed to work nicely in GC. You need `sip` version `4.19.x`. At
thetime of writing [they say][gc-python-wiki] `4.19.8`. (TODO: Try newer `4.19`
ones).

You also need to be using Python 3.7. Idk if the minor number matters, I ended
up being explicit with that one too.

I (or my older scripts anyway) also use plotly. Also numpy. I'll have to see
whether there are any others.

Install them

```
/opt/miniconda3.7-gc/bin/conda install python=3.17.15 sip=4.19.8 plotly numpy
```


[gc-python-wiki]: https://github.com/GoldenCheetah/GoldenCheetah/wiki/UG_Special-Topics_Working-with-Python
