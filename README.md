Editable Replace
============

This plugin for Sublime Text 2/3 uses the "Find Results" view to perform replacing. That is, you use
Find in Files first to search what should be replaced, which opens the "Find Results" view. Then,
you edit the results as desired (remove lines you want to exclude from replacing and edit lines that
should be replaced). Finally you perform the replacement, i.e. the affected lines are replaced with
their current content in the "Find Results" view.

This has a couple of advantages:

1. You don't need to come up with an exact pattern that includes all occurrences that should be
replaced *and* excludes all that should not be replaced. Since this can be hard sometimes, this
plugin is handy because you can first do a broader search and select afterwards what occurrences
should actually be replaced.
2. Although you search for one pattern, you can replace all occurrences individually.
3. As replacing is prepared like editing a file, you have all the powerful features of ST at hand,
like "Expand Selection to Word" etc.
4. It saves time, because in contrast to the builtin "Replace in Files" of ST, it does not open all
changed files (unsaved) after the replace. This is not necessary with Editable Replace because you
view and select all changes before applying them.
5. In ST2, "Replace in Files" was really slow, while this plugin performs the changes very fast.


Keymap:
---

Editable Replace comes also with a keymap, which is by default configured as follows:

- super+R: replace all
- super+F: replace in current file (in "Find Results", everything is grouped by file)
- super+V: replace current line
- super+shift+R: delete all
- super+shift+F: delete in current file
- super+shift+V: delete current line


Installation:
---

Just clone this git repo into your Packages folder.


Recommendations:
---

Although Editable Replace works with and without enabling "Context" when using Find in Files, I
personally find the plugin easier to use when it is turned off.
