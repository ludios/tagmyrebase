#!/usr/bin/env python

"""
Utility to mark the HEAD with a branch and timestamped tag, and the upstream
commit (that we're rebased on top of) with another timestamped tag.  All three
markings are optional.

This allows you to

1) easily find an older set of rebased patches with `git tag`
2) see in tig/gitk which commits you've previously rebased onto.
"""

__version__ = '0.1'

import sys
import datetime
import subprocess
import argparse
import pprint


def call(cmd):
	return subprocess.check_call(cmd)


def get_expanded_name(format_string, t):
	return format_string % dict(YMDHMS=t.strftime('%Y-%m-%d_%H-%M-%S'))


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
		assert _ == "", repr(_)
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


def get_commit_or_none(branch_name):
	try:
		return get_commit(branch_name)
	except subprocess.CalledProcessError, e:
		# fatal: ambiguous argument 'some-branch': unknown revision or path not in the working tree.
		if not 'returned non-zero exit status 128' in str(e):
			raise
		return None


def now():
	return datetime.datetime.now()


def main():
	parser = argparse.ArgumentParser(description="""
	Utility to mark the HEAD with a branch and timestamped tag, and the upstream
	commit (that we're rebased on top of) with another timestamped tag.  All three
	markings are optional.

	This allows you to

	1) easily find an older set of rebased patches
	2) see in tig/gitk which commits you've previously rebased onto.

	For an of --tag-head, --branch-head, and --tag-upstream, you can use
	%(YMDHMS)s to insert the current time.
	""")

	parser.add_argument('-t', '--tag-head', dest='tag_head',
		help="create a tag with this name pointing to HEAD")

	parser.add_argument('-b', '--branch-head', dest='branch_head',
		help="force-create a branch with this name pointing to HEAD")

	parser.add_argument('-u', '--tag-upstream', dest='tag_upstream',
		help="create a tag with this name pointing to the upstream commit")

	args = parser.parse_args()

	if not (args.tag_head or args.branch_head or args.tag_upstream):
		print >>sys.stderr, ("Must specify one or more of --tag-head, "
			"--branch-head, or --tag-upstream; see --help")
		sys.exit(1)

	#branch_name = args.branch_name
	#if get_commit_or_none(branch_name) == get_commit("HEAD"):
	#	print >>sys.stderr, "HEAD is already marked as %s" % (branch_name,)
	#else:

	t = now()

	if args.branch_head:
		call(["git", "branch", "-f", get_expanded_name(args.branch_head, t)])

	if args.tag_head or args.tag_upstream:
		upstream_commit = get_upstream_commit()

	if args.tag_upstream:
		call(["git", "tag", "-a", "--message", "",
			get_expanded_name(args.tag_upstream, t), upstream_commit])

	if args.tag_head:
		call(["git", "tag", "-a", "--message", get_tag_message(upstream_commit),
			get_expanded_name(args.tag_head, t)])


if __name__ == '__main__':
	main()
