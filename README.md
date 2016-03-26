# PyDucky

PyDucky is a Python 3 version of the original [RubberDucky](https://github.com/hak5darren/USB-Rubber-Ducky) script encoder (Java).

This version allows you to use alternative layout. It supports ASCII, ISO-8859-1 and Unicode.

```bash
$ python3 pyducky.py -i script.txt

or

$ python3 pyducky.py -i script.txt -o inject.bin -l fr
```

> **Note**
> This is a *beta* version, I didn't run all the necessary tests...

## Setup

This tool requires the [PyYAML](http://pyyaml.org) module.

```bash
$ pip3 install PyYAML
```


```bash
Usage: pyducky.py [options]

Options:
  -h, --help            show this help message and exit
  -i INFILE, --input=INFILE
                        DuckyScript file
  -o OUTFILE, --output=OUTFILE
                        Output filename (default: inject.bin)
  -l LAYOUT, --layout=LAYOUT
                        Keyboard layout file (us/fr/ca/etc. default: us)
```
   
## Resources

[Original project](https://github.com/hak5darren/USB-Rubber-Ducky)

Ducky Script [syntax](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript)

## License

This project is released under the Apache 2 license. See LICENCE file.