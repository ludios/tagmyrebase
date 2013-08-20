#!/usr/bin/env python

"""
Utility to mark the HEAD with a branch and timestamped tag, and the upstream
commit (that we're rebased on top of) with another timestamped tag.

This allows you to

1) easily find an older set of rebased patches with `git tag`
2) see in tig/gitk which commits you've previously rebased onto.
"""

import sys
import datetime
import subprocess
import argparse
import pprint


def call(cmd):
	return subprocess.check_call(cmd)


def get_tag_name(branch_name, t):
	return branch_name + "-" + t.strftime('%Y-%m-%d_%H-%M-%S')


def get_tag_message(upstream_commit):
	# Annotated tag already has tagger name, e-mail, and date
	# TODO XXX: what if this date doesn't match the date that Python gets?
	# Should we use a courser-grained tag name that doesn't include the full timestamp?
	# Or set GIT_COMMITTER_DATE for git tag
	return "Onto: %s\n" % (upstream_commit,)


def get_reflog_entries(branch_name):
	for line in open(".git/logs/" + branch_name, "rb"):
		before_email, after_email = line.split(">", 1)
		before_email += ">"
		old, new, email = before_email.split(" ", 2)
		_, date, tz = after_email.split("\t", 1)[0].split(" ", 2)
		message = after_email.split("\t", 1)[1]
		yield dict(old=old, new=new, email=email, date=date, tz=tz, message=message)


def get_upstream_commit():
	"""
	Return the upstream commit that our patches (if we have any) are rebased on top of.
	"""
	entries = list(reversed(list(get_reflog_entries("HEAD"))))

	for entry in entries:
		# TODO: add more verification that the rebase finished? (and for the right branch)
		if entry["message"].startswith("checkout: moving from "):
			return entry["new"]

	raise RuntimeError(
		"Could not find upstream commit in reflog; "
		"entries are:\n%s" % (pprint.pformat(entries),))


def get_commit(branch_name):
	return subprocess.check_output(["git", "rev-parse", branch_name]).split()[0]


def now():
	return datetime.datetime.now()


def main():
	parser = argparse.ArgumentParser(description="""
	Utility to mark the HEAD with a branch and timestamped tag, and the upstream
	commit (that we're rebased on top of) with another timestamped tag.

	This allows you to

	1) easily find an older set of rebased patches
	2) see in tig/gitk which commits you've previously rebased onto.
	""")

	parser.add_argument('-m', '--mark', dest='branch_name',
		help="force-create a branch with this name pointing to HEAD, mark "
		     "it with a timestamped tag; also mark the upstream commit with a timestamped tag")

	args = parser.parse_args()

	if args.branch_name:
		branch_name = args.branch_name
		if get_commit(branch_name) == get_commit("HEAD"):
			print >>sys.stderr, "HEAD is already marked as %s" % (branch_name,)
		else:
			upstream_commit = get_upstream_commit()
			t = now()
			call(["git", "branch", "-f", branch_name])
			# Mark the upstream commit (use a short "U-" prefix to avoid long tag names.)
			call(["git", "tag", "-a", "--message", "",
				"U-" + get_tag_name(branch_name, t), upstream_commit])
			# Mark the downstream commit
			call(["git", "tag", "-a", "--message", get_tag_message(upstream_commit),
				get_tag_name(branch_name, t)])
	else:
		print >>sys.stderr, "Must specify --mark branchname; see --help"

# TODO: add command to mark upstream branch as good, even if we can't yet
# rebase our patchset on top of it?


if __name__ == '__main__':
	main()
