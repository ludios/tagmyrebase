<!-- clank-right
languages     = ["python"]
python_indent = "tabs"
-->

# Before committing

There are no automated tests, so at least run `./tagmyrebase --help`, which shows that the script still parses and builds its argument parser.

To try a change for real, don't run `tagmyrebase` in this repository, because it would create tags here (and, with `--branch-head`, create or move a branch here). Instead, under /tmp: make an "upstream" repository, clone it, commit a patch in the clone, add a commit to the upstream repository, run `git pull --rebase` in the clone, and then run `tagmyrebase` in the clone. (`test/make-dummy-commit` reads /usr/share/dict/words, which this machine doesn't have.)
