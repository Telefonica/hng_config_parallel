from fileinput import FileInput
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

import os
import re
import sys
import yaml

HNG = 'src/templates/hng'
HNGv4 = 'src/templates/hng4'
COMMON = os.getcwd ()

class Scripter:
    """Provides methods for Rural GW script generation.

    Attributes:
        src (str): The name of the YAML file.
        dest (str): The name of the file where to save the script.
        device (str): The device name.
        comments (bool): Includes the comments or not.
        headers (bool): Includes the headers or not.

    """
    def __init__(self, src, dest, device, comments, headers):
        with open(src, 'r') as stream:
            try:
                self.config = yaml.load(stream, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        self.src = src
        self.dest = dest
        self.device = device
        self.comments = comments
        self.headers = headers
        self.path = 'templates/'
        self.mode = 'user'
        print ("src %s", self.src)
        print ("dest %s", self.dest)
        print ("device %s", self.device)
        print ("comments %s", self.comments)
        print ("headers %s", self.headers)

    def clean_file(self, dest):
        """Allows to delete the different indentations of lines present
        in a given file.

        Args:
            dest (str): The destination file.

        """
        clean_lines = []
        with open(dest, "r") as f:
           clean_lines = [line.strip() for line in f.readlines()]

        with open(dest, "w") as f:
            f.writelines('\n'.join(clean_lines))

    def create_header(self, title, delimitor='!', limit=71):
        """Creates a header based on a title, delimiter and line size
        limit.

        Args:
            title (str): The header title.
            delimitor (str): The delimiter symbol.
            limit (int): The maximum font size per line.

        Returns:
            str: The header.

        """
        symbols = round((limit - len(title)) / 2)
        return delimitor * symbols + ' ' + title.upper() + ' ' + delimitor * symbols

    def yaml_parse(self, value):
        """Returns whether the key is defined or not
        Args:
            value: The key value in the yaml to be parsed
        Returns:
            Boolean: True if value with template, false otherwise
        """
        if self.device=='hng':
            switcher = {
                "gateway": True,
                "core": True,
                "pports": True,
                "sports": True,
                "pinterfaces": True,
                "sinterfaces": True,
                "virtualnetworks": True,
                "cluster": True,
                "certificates": True
            }
        else:
            switcher = {
                "venb": True,
                "zone": True,
                "ports": True,
                "vrnc": True,
                "ipsec": True,
                "virtualnetworks": True,
                "system": True,
                "cluster": True,
                "certificates": True
            }
        return switcher.get(value, False)

    def create_file(self, dest, config, env):
        """Creates the file containing all the necessary Rural GW
        templates.

        Args:
            dest (str): The absolute path to the file to be created.
            config (dict): The configuration file.
            env (Environment): The Jinja2 environnement.

        """
        if len(env.list_templates()) > 0:
            open(dest, 'w').close()
        else:
            print("Error: No templates available.")
            sys.exit(1)


    def create_filev4(self, dest, config, env):
        """Creates the file containing all the necessary Rural GW
        templates.

        Args:
            dest (str): The absolute path to the file to be created.
            config (dict): The configuration file.
            env (Environment): The Jinja2 environnement.

        """
        if len(env.list_templates()) > 0:
            open(dest, 'w').close()
        else:
            print("Error: No templates available.")
            sys.exit(1)

        if config is None:
            print("Error: No sections in YAML file ({})".format(self.src))
            sys.exit(1)
            
        for section in config:
            print ("section inside config is: %s", section)
            if ((section == 'hngv4')): 
                self.enter_conft(dest)
            else:
                print("Error: YAML file error")
                sys.exit(1)
                
            for key in config[section]:    
                print ("key inside section is:", key)  
                if self.yaml_parse(key): 
                    template = env.get_template('hng4/' + key + '.txt')
                else:
                    print ("Error: No Rural GW template available")
                    sys.exit(1)
                
                if len(template.render(self.config)) > 0 and key != 'group' and key != 'encryption':
                    if key != 'save':
                        self.write_text(dest, template.render(self.config) + '\n')
                    else:
                        self.write_text(dest, template.render(self.config) + '\n')

            if self.mode == 'conft':
                self.exit_conft(dest)
            if self.mode == 'enable':
                self.exit_enable(dest)


    def enter_primary_node(self, dest):
        """Enter into system primary node in the hng.
        Args:
            dest: The destination filename to write.
        """
        self.mode = 'node'
        self.write(dest, HNGv4 + '/pnode.txt')

    def enter_secondary_node(self, dest):
        """Enter into system secondary node in the hng.
        Args:
            dest: The destination filename to write.
        """
        self.mode = 'node'
        self.write(dest, HNGv4 + '/snode.txt')    

    #def enter_enable(self, dest):
        """Adds the enable mode to the specified file and updates the
        current mode.

        Args:
            dest: The destination filename to write.

        """
    #    self.mode = 'enable'
    #    self.write(dest, COMMON + '/enable.txt')

    def enter_conft(self, dest):
        """Adds the configuration terminal mode to the specified file
        and updates the current mode.

        Args:
            dest: The destination filename to write.

        """
        self.mode = 'conft'
        self.write(dest, HNGv4 + '/conft.txt')

    def exit_conft(self, dest):
        """Exits the configuration terminal mode to the specified file
        and updates the current mode.

        Args:
            dest: The destination filename to write.

        """
        self.mode = 'enable'
        self.write(dest, HNGv4 + '/exit_conft.txt')

    def exit_enable(self, dest):
        """Exits the enable mode to the specified file and updates the
        current mode.

        Args:
            dest: The destination filename to write.

        """
        #self.mode = 'user'
        #self.write(dest, HNGv4 + '/exit_enable.txt')

    def exit_specific(self, dest):
        """Exits the specifc mode to the specified file and updates the current
        mode.

        Args:
            dest: The destination filename to write.

        """
        self.mode = 'conft'
        self.write(dest, COMMON + '/exit_spec.txt')

    def remove_comments(self, dest):
        """Removes the comments in a file, except headers.

        Args:
            dest: The destination filename to read.

        """
        with open(dest, 'r') as f:
            no_comments = [line.strip() for line in f if line.count('!') == 0 or line.count('!') > 1]

        for i in range(len(no_comments)):
            if '!' in no_comments[i] and i > 0:
                no_comments[i] = '\n' + no_comments[i]

        with open(self.dest, 'w') as f:
            [f.write(line + '\n') for line in no_comments]

    def remove_headers(self, dest):
        """Removes the headers in a file.

        Args:
            dest: The destination filename to read.

        """
        with open(dest, 'r') as f:
            no_comments = [line.strip() for line in f if line.count('!') == 0 or line.count('!') == 1]

        with open(self.dest, 'w') as f:
            [f.write(line + '\n') for line in no_comments]

    def run(self, verbose=True):
        """Generates the script for the device according to a config
        file.

        Args:
           verbose (bool, optional): Outputs or not the script to the
           console (default: False).

        """
        print (self.path)

        env = Environment(
            loader=PackageLoader('src', self.path),
            trim_blocks=True,
            lstrip_blocks=True
        )
        print (self.config)

        if self.device == 'hng':
            self.create_file(self.dest, self.config, env)
        elif self.device == 'hngv4':
            self.create_filev4(self.dest, self.config, env)
        else:
            print ("create file not available")

        if not self.comments:
            self.remove_comments(self.dest)
        if not self.headers:
            self.remove_headers(self.dest)
        self.clean_file(self.dest)

        if verbose:
            with open(self.dest, 'r') as output_file:
               print(output_file.read())

    def write(self, dest, src):
        """Writes the content of a file in a destination file.

        Args:
            dest (str): The destination file.
            text (str): The text file.

        """
        with open(dest, "a") as dest_file:
            with open(src, 'r') as src_file:
                dest_file.write(src_file.read() + '\n')

    def write_text(self, dest, text):
        """Writes text in a destination file.

        Args:
            dest (str): The destination file.
            text (str): The text file.

        """
        with open(dest, "a") as dest_file:
            dest_file.write(text)
