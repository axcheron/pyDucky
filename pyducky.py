#!/usr/bin/python3

""" pyducky.py: Encode RubberDucky Scripts (Based on Java Version)"""

__author__ = 'axcheron'
__license__ = 'Apache 2'
__version__ = '0.1'

from optparse import OptionParser
from os import path
from sys import exit
from yaml import safe_load, YAMLError


class Encode:
    """This class is used to encode ducky scripts to binary files"""

    def __init__(self, in_fname, out_fname, layout):
        """
        Set the default attributes.

        :param in_fname: String. Ducky script filename.
        :param out_fname: String. Destination filename
        :param layout: String. Keyboard layout.
        """

        self.script = in_fname
        self.out = out_fname
        self.layout = layout
        self.byte_array = bytearray()

        self.kprop = None
        self.lprop = None
        self.data = None

        if self.load_files():
            self.encode_to_file()
        else:
            exit(-1)


    def load_files(self):
        """
        Load layout files and ducky script.

        :return: Boolean
        """

        # Load YAML files
        try:
            self.kprop = safe_load(open("resources/default.yml", 'r'))
            self.lprop = safe_load(open("resources/" + self.layout + ".yml", 'r'))
        except IOError as fexc:
            print(fexc)
            return False
        except YAMLError as yexc:
            print("[Exception] Error in YAML files", yexc)
            return False

        # Load DuckyScript
        try:
            h_file = open(self.script, 'r')
            self.data = h_file.read()
            h_file.close()
        except IOError as fexc:
            print(fexc)
            return False

        return True


    def encode_to_file(self):

        default_delay = 0
        last_inst = None
        repeat = False
        data = None
        loop = 0

        self.data = self.data.replace('\r', '')
        instruction_list = self.data.split('\n')

        for index, inst in enumerate(instruction_list):
            try:
                delay_override = False

                # Check comment
                if inst[:2] == '//':
                    continue

                # Check newline
                if inst == '\n':
                    continue

                # Backup last instruction for REPEAT
                if last_inst is not None:
                    last_inst = instruction_list[index - 1].split(' ', 1)
                    last_inst[0] = last_inst[0].strip()

                    if len(last_inst) == 2:
                        last_inst[1] = last_inst[1].strip()
                else:
                    last_inst = inst.split(' ', 2)
                    last_inst[0] = last_inst[0].strip()

                    if len(last_inst) == 2:
                        last_inst[1] = last_inst[1].strip()

                # Handling current instruction
                instruction = inst.split(' ', 1)
                instruction[0] = instruction[0].strip()

                if len(instruction) == 2:
                    instruction[1] = instruction[1].strip()

                if instruction[0] == "REM":
                    continue

                if instruction[0] == "REPEAT":
                    loop = int(instruction[1])
                    repeat = True
                else:
                    repeat = False
                    loop = 1

                # Start encoding
                while loop > 0:
                    if repeat:
                        instruction = last_inst

                    # Handle DEFAULT_DELAY
                    if instruction[0] == "DEFAULT_DELAY" or instruction[0] == "DEFAULTDELAY":
                        default_delay = int(instruction[1])
                        delay_override = True

                    # Handle DELAY
                    elif instruction[0] == "DELAY":
                        delay = int(instruction[1])

                        while delay > 0:
                            self.byte_array.append(0x00)

                            if delay > 255:
                                self.byte_array.append(0xFF)
                                delay -= 255

                            else:
                                self.byte_array.append(delay)
                                delay = 0

                        delay_override = True

                    # Handle STRING
                    elif instruction[0] == "STRING":
                        try:
                            for c in instruction[1]:
                                for d in self.char_to_bytes(c):
                                    self.byte_array.append(d)

                                if len(self.char_to_bytes(c)) % 2 != 0:
                                    self.byte_array.append(0x00)
                        except IndexError:
                            pass

                    # Handle CTRL
                    elif instruction[0] == "CONTROL" or instruction[0] == "CTRL":
                        if len(instruction) != 1:
                            self.byte_array.append(self.inst_to_byte(instruction[1]))
                            self.byte_array.append(self.kprop["MODIFIERKEY_CTRL"])
                        else:
                            self.byte_array.append(self.kprop["KEY_LEFT_CTRL"])
                            self.byte_array.append(0x00)

                    # Handle ALT
                    elif instruction[0] == "ALT":
                        if len(instruction) != 1:
                            self.byte_array.append(self.inst_to_byte(instruction[1]))
                            self.byte_array.append(self.kprop["MODIFIERKEY_ALT"])
                        else:
                            self.byte_array.append(self.kprop["KEY_LEFT_ALT"])
                            self.byte_array.append(0x00)

                    # Handle SHIFT
                    elif instruction[0] == "SHIFT":
                        if len(instruction) != 1:
                            self.byte_array.append(self.inst_to_byte(instruction[1]))
                            self.byte_array.append(self.kprop["MODIFIERKEY_SHIFT"])
                        else:
                            self.byte_array.append(self.kprop["KEY_LEFT_SHIFT"])
                            self.byte_array.append(0x00)

                    # Handle CTRL-ALT
                    elif instruction[0] == "CTRL-ALT":
                        if len(instruction) != 1:
                            self.byte_array.append(self.inst_to_byte(instruction[1]))
                            self.byte_array.append(self.kprop["MODIFIERKEY_CTRL"] | self.kprop["MODIFIERKEY_ALT"])
                        else:
                            continue

                    elif instruction[0] == "CTRL-SHIFT":
                        if len(instruction) != 1:
                            self.byte_array.append(self.inst_to_byte(instruction[1]))
                            self.byte_array.append(self.kprop["MODIFIERKEY_CTRL"] | self.kprop["MODIFIERKEY_SHIFT"])
                        else:
                            continue

                    elif instruction[0] == "COMMAND-OPTION":
                        if len(instruction) != 1:
                            self.byte_array.append(self.inst_to_byte(instruction[1]))
                            self.byte_array.append(self.kprop["MODIFIERKEY_KEY_LEFT_GUI"] | self.kprop["MODIFIERKEY_ALT"])
                        else:
                            continue

                    elif instruction[0] == "ALT-SHIFT":
                        if len(instruction) != 1:
                            self.byte_array.append(self.inst_to_byte(instruction[1]))
                            self.byte_array.append(self.kprop["MODIFIERKEY_LEFT_ALT"] | self.kprop["MODIFIERKEY_SHIFT"])
                        else:
                            self.byte_array.append(self.kprop["KEY_LEFT_ALT"])
                            self.byte_array.append(self.kprop["MODIFIERKEY_LEFT_ALT"] | self.kprop["MODIFIERKEY_SHIFT"])

                    elif instruction[0] == "ALT-TAB":
                        if len(instruction) == 1:
                            self.byte_array.append(self.kprop["KEY_TAB"])
                            self.byte_array.append(self.kprop["MODIFIERKEY_LEFT_ALT"])

                    elif instruction[0] == "REM":
                        delay_override = True
                        continue

                    elif instruction[0] == "WINDOWS" or instruction[0] == "GUI":
                        if len(instruction) == 1:
                            self.byte_array.append(self.kprop["MODIFIERKEY_LEFT_GUI"])
                            self.byte_array.append(0x00)
                        else:
                            self.byte_array.append(self.inst_to_byte(instruction[1]))
                            self.byte_array.append(self.kprop["MODIFIERKEY_LEFT_GUI"])

                    elif instruction[0] == "COMMAND":
                        if len(instruction) == 1:
                            self.byte_array += self.kprop["KEY_COMMAND"]
                            self.byte_array.append(0x00)
                        else:
                            self.byte_array.append(instruction[1])
                            self.byte_array += self.kprop["MODIFIERKEY_LEFT_GUI"]

                    # Empty Line
                    elif instruction[0] == '':
                        pass

                    else:
                        self.byte_array.append(self.inst_to_byte(instruction[0]))
                        self.byte_array.append(0x00)

                    loop -= 1

                # Adding default delay
                if not delay_override and default_delay > 0:
                    delay_counter = default_delay

                    while delay_counter > 0:
                        self.byte_array.append(0x00)

                        if delay_counter > 255:
                            self.byte_array.append(0xFF)
                            delay_counter -= 255

                        else:
                            self.byte_array.append(delay_counter)
                            delay_counter = 0

            except Exception as e:
                print("/!\\ Exception \"%s\" at line %d" % (e, index+1))

        try:
            fh = open(self.out, 'wb')
            fh.write(self.byte_array)
            fh.close()
        except Exception as e:
            print(e)


    def char_to_bytes(self, char):
        return self.code_to_bytes(self.char_to_code(char))


    def char_to_code(self, char):

        if ord(char) < 128:
            code = "ASCII_" + format(ord(char), 'x').upper()
        elif ord(char) < 256:
            # ISO 8859-1 is also known as Latin-1
            code = "ISO_8859_1_" + format(ord(char), 'x').upper()
        else:
            code = "UNICODE_" + format(ord(char), 'x').upper()

        return code


    def code_to_bytes(self, code):

        byte = list()

        if code in self.lprop:
            for key in self.lprop[code]:

                if key in self.kprop:
                    byte.append(self.kprop[key])
                elif key in self.lprop:
                    byte.append(self.lprop[key])
                else:
                    print("Key Not Found: ", key)
                    byte.append(0x00)

            return byte

        else:
            print("Character Not Found: ", code)
            byte.append(0x00)
            return byte


    def inst_to_byte(self, instruction):
        instruction = instruction.strip()

        if "KEY_" + instruction in self.kprop.keys():
            return self.kprop["KEY_" + instruction]
        if instruction == "ESCAPE":
            return self.inst_to_byte("ESC")
        if instruction == "DEL":
            return self.inst_to_byte("DELETE")
        if instruction == "BREAK":
            return self.inst_to_byte("PAUSE")
        if instruction == "CONTROL":
            return self.inst_to_byte("CTRL")
        if instruction == "DOWNARROW":
            return self.inst_to_byte("DOWN")
        if instruction == "UPARROW":
            return self.inst_to_byte("UP")
        if instruction == "LEFTARROW":
            return self.inst_to_byte("LEFT")
        if instruction == "RIGHTARROW":
            return self.inst_to_byte("RIGHT")
        if instruction == "MENU":
            return self.inst_to_byte("APP")
        if instruction == "WINDOWS":
            return self.inst_to_byte("GUI")
        if instruction == "PLAY" or instruction == "PAUSE":
            return self.inst_to_byte("MEDIA_PLAY_PAUSE")
        if instruction == "STOP":
            return self.inst_to_byte("MEDIA_STOP")
        if instruction == "MUTE":
            return self.inst_to_byte("MEDIA_MUTE")
        if instruction == "VOLUMEUP":
            return self.inst_to_byte("MEDIA_VOLUME_INC")
        if instruction == "VOLUMEDOWN":
            return self.inst_to_byte("MEDIA_VOLUME_DEC")
        if instruction == "SCROLLLOCK":
            return self.inst_to_byte("SCROLL_LOCK")
        if instruction == "NUMLOCK":
            return self.inst_to_byte("NUM_LOCK")
        if instruction == "CAPSLOCK":
            return self.inst_to_byte("CAPS_LOCK")

        return self.char_to_bytes(instruction[0])[0]


if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option("-i", "--input", dest="infile", action="store",
                      help="DuckyScript file", type="string")

    parser.add_option("-o", "--output", dest="outfile", action="store",
                      help="Output filename (default: inject.bin)", default="inject.bin", type="string")

    parser.add_option("-l", "--layout", dest="layout", action="store",
                      help="Keyboard layout file (us/fr/ca/etc. default: us)", default="us", type="string")

    (options, args) = parser.parse_args()

    if options.infile is None:
        parser.print_help()
        exit(-1)
    elif not path.exists(options.infile):
        parser.error("input file '%s' does not exist" % options.infile)
    else:
        encode = Encode(options.infile, options.outfile, options.layout)

