import sublime, sublime_plugin
import re

class EditableReplaceCommand(sublime_plugin.TextCommand):
    def __init__(self, arg):
        super(EditableReplaceCommand, self).__init__(arg)
        self.path_regex = re.compile(r"^([^#]\S+):")
        self.repl_regex = re.compile(r"^\s+(\d+): (.*?)$")

    def is_visible(self):
        return self.view.file_name() == None and self.view.name() == "Find Results"

    def get_lines(self, text):
        prev_pos = -1
        while True:
            pos = text.find('\n', prev_pos + 1)
            if pos < 0:
                break
            yield (text[prev_pos + 1:pos], prev_pos + 1)
            prev_pos = pos

    def get_replace(self, replaces, lineno):
        for r in replaces:
            if r[0] == lineno:
                return r[1]
        return False

    def replace_line(self, f, content, replaces):
        i = 1
        for line in self.get_lines(content):
            repl = self.get_replace(replaces, i)
            if repl != False:
                if not self.modedel:
                    f.write(repl + "\n")
            else:
                f.write(line[0] + "\n")
            i += 1

    def replace_file(self, filename, replaces):
        # read current content
        try:
            f = open(filename, "r")
            content = f.read()
            f.close()

            # overwrite with replacement
            try:
                f = open(filename, "w")
                self.replace_line(f, content, replaces)
                self.replaces += len(replaces)
                self.files += 1
                f.close()
            except IOError as e:
                print("writing failed: " + str(e))
        except IOError as e:
            print("reading failed: " + str(e))

    def mark_replaced(self, text, start, end):
        pos = start - 1
        while pos < end:
            next = text.find('\n', pos + 1)
            line = text[pos + 1:next]
            # only mark the line if it's a replace-line or path-line
            if self.path_regex.match(line) or self.repl_regex.match(line):
                self.view.insert(self.edit, pos + 1 + self.off, '#')
                self.off += 1
            pos = next

    def apply_replace(self, text, cur_file, replaces, start_pos, end_pos):
        if cur_file != "" and len(replaces) > 0:
            self.replace_file(cur_file, replaces)
            self.mark_replaced(text, start_pos, end_pos)

    def replace_all(self, text):
        i = 0
        start_pos = 0
        end_pos = 0
        cur_file = ""
        replaces = []
        for line in self.get_lines(text):
            if line[0].strip() != "":
                res = self.path_regex.match(line[0])
                if res:
                    self.apply_replace(text, cur_file, replaces, start_pos, end_pos)
                    cur_file = res.group(1)
                    replaces = []
                    start_pos = line[1]
                elif cur_file != "":
                    res = self.repl_regex.match(line[0])
                    if res:
                        replaces.append((int(res.group(1)), res.group(2)))
                        end_pos = line[1]
            i += 1
        self.apply_replace(text, cur_file, replaces, start_pos, end_pos)

    def find_last_file(self, pos):
        while pos > 0:
            line = self.view.line(pos)
            linetext = self.view.substr(line)
            res = self.path_regex.match(linetext)
            if res:
                return (res.group(1), line.a)
            # if there is a commented out path line, stop here. because probably we are in a already
            # replaced file-block and walking to the previous one is unintuitive.
            if len(linetext) > 0 and linetext[0] == '#' and self.path_regex.match(linetext[1:]):
                break
            pos = line.a - 1
        return None

    def find_file_end(self, pos):
        while pos < self.view.size():
            line = self.view.line(pos)
            linetext = self.view.substr(line)
            if linetext.strip() == "":
                return line.a
            pos = line.b + 1
        return self.view.size() - 1

    def find_next_repl(self, pos):
        while pos < self.view.size():
            line = self.view.line(pos)
            linetext = self.view.substr(line)
            if self.repl_regex.match(linetext):
                return pos
            pos = line.b + 1
        return self.view.size() - 1

    def run(self, edit, mode = "all", modedel = False):
        self.edit = edit
        self.off = 0
        self.files = 0
        self.replaces = 0
        self.modedel = modedel;

        buffer_text = self.view.substr(sublime.Region(0,self.view.size() - 1))
        sel = self.view.sel()

        filename = None
        if mode == "all":
            # no selection?
            if len(sel) == 1 and sel[0].a == sel[0].b:
                self.replace_all(buffer_text)
            else:
                for s in sel:
                    self.off = min(s.a, s.b)
                    self.replace_all(self.view.substr(s))
        else:
            filename = self.find_last_file(min(sel[0].a, sel[0].b))
            if filename == None:
                print("Unable to find filename")
                return

            # replace current line
            if mode == "line":
                line = self.view.line(sel[0])
                linetext = self.view.substr(line)
                res = self.repl_regex.match(linetext)
                if res:
                    replaces = [(int(res.group(1)), res.group(2))]
                    self.apply_replace(buffer_text, filename[0], replaces, line.a, line.b)
                    # set cursor to next replace-line
                    sel.clear()
                    pos = self.find_next_repl(line.b + 2)
                    sel.add(sublime.Region(pos, pos))
                else:
                    print("Line has unexpected form")
            # replace current file
            else:
                end = self.find_file_end(filename[1])
                text = self.view.substr(sublime.Region(filename[1], end))
                self.off = filename[1]
                self.replace_all(text)
                # set cursor to next file
                sel.clear()
                nextfile_pos = end + self.off - filename[1] + 1
                sel.add(sublime.Region(nextfile_pos, nextfile_pos))

        op = "Deleted" if self.modedel else "Replaced"
        if filename != None:
            print(op + " " + str(self.replaces) + " lines in " + filename[0] + ".")
        else:
            print(op + " " + str(self.replaces) + " lines in " + str(self.files) + " files.")

class EditableReplaceEventListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "editable_replace_is_enabled" and view != None:
            return view.file_name() == None and view.name() == "Find Results"
        return None
