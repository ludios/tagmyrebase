#!/usr/bin/env python

"""
Utility to mark the HEAD with a branch and timestamped tag, and the upstream
commit (that we're rebased on top of) with another timestamped tag.

This allows you to

1) easily find an older set of rebased patches with `git tag`
2) see in tig/gitk which commits you've previously rebased onto.  This is
   useful for seeing which new commits you might need to review.

Sample usage:
git pull --rebase
tagmyrebase.py --tag-upstream 'U-{YMDN}' --tag-head 'good-{YMDN}' --branch-head good

All three arguments are optional.

For any of --tag-upstream, --tag-head, and --branch-head, you can use {YMDHMS}
to insert the current time, or {YMDN} to insert the current date with a
counter that avoids collision with existing tags.  Note that the {YMDHMS} or
{YMDN} will not necessarily correspond on the HEAD and upstream commits.
"""

__version__ = '0.4'

import re
import sys
import datetime
import subprocess
import argparse


def get_re_for_format_string(format_string):
	"""
	Returns a regular expression for a format string, so that we can check
	if a tag already exists.
	"""
	YMDHMS_RE = r'\d\d\d\d-[01]\d-[0-3]\d_[0-2]\d-[0-5]\d-[0-6]\d'
	YMDN_RE = r'\d\d\d\d-[01]\d-[0-3]\d\.\d+'
	return re.compile(
		r'\A' +
		format_string
			.replace('{YMDHMS}', YMDHMS_RE)
			.replace('{YMDN}', YMDN_RE) +
		r'\Z')


def memoize(f):
	class memodict(dict):
		def __missing__(self, key):
			ret = self[key] = f(key)
			return ret
	return memodict().__getitem__


@memoize
def get_commit_message(commit):
	_, message = subprocess.check_output(
		["git",  "log", "--format=oneline", "--max-count=1", commit]).split(" ", 1)
	message = message.rstrip("\r\n")
	if _ != commit:
		raise RuntimeError("git log returned the wrong commit: %r %r" % (_, message))
	return message


def get_refs():
	stdout = subprocess.check_output(["git", "show-ref", "--head", "--dereference"])
	refs = dict(tags={}, heads={}, HEAD=None)
	lines = stdout.replace("\r", "").strip("\n").split("\n")
	DEREF = "^{}"
	for line in lines:
		commit, ref = line.split(" ", 1)
		if ref.startswith("refs/tags/") and ref.endswith(DEREF):
			# Grab only the dereference lines ending with ^{} because
			# we only care about the objects the tags point to, not the
			# tags themselves.
			refs["tags"][ref.replace("refs/tags/", "", 1)[:-len(DEREF)]] = commit
		elif ref.startswith("refs/heads/"):
			refs["heads"][ref.replace("refs/heads/", "", 1)] = commit
		elif ref == "HEAD":
			refs["HEAD"] = commit
		# We don't need remotes
	return refs


def get_names_on_commit(commit, type, refs):
	assert type in ("tags", "heads"), type
	NAME = 0
	COMMIT_ID = 1
	return list(t[NAME] for t in refs[type].iteritems() if t[COMMIT_ID] == commit)


def get_expanded_name(format_string, t, refs):
	ymdn = None
	if '{YMDN}' in format_string:
		ymd = t.strftime('%Y-%m-%d')
		for n in xrange(1, 100000):
			proposed_ymdn = ymd + '.' + str(n)
			proposed_tag = get_expanded_name(
				format_string.format(
					YMDN=proposed_ymdn,
					YMDHMS='{YMDHMS}'
				), t, refs)
			if not proposed_tag in refs["tags"]:
				ymdn = proposed_ymdn
				break
		else:
			raise RuntimeError("100,000 tags in one day is too many tags")

	return format_string.format(
		YMDN=ymdn,
		YMDHMS=t.strftime('%Y-%m-%d_%H-%M-%S')
	)


def make_tag_message(upstream_commit):
	# Annotated tag already has tagger name, e-mail, and date
	# TODO XXX: what if this date doesn't match the date that Python gets?
	# Maybe set GIT_COMMITTER_DATE for git tag
	return "Onto: %s\n" % (upstream_commit,)


def get_reflog_entries(branch_name):
	# show_one_reflog_ent https://github.com/git/git/blob/master/refs.c#L2985
	for line in open(".git/logs/refs/heads/" + branch_name, "rb"):
		before_email, after_email = line.split(">", 1)
		before_email += ">"
		old, new, email = before_email.split(" ", 2)
		_, date, tz = after_email.split("\t", 1)[0].split(" ", 2)
		message = after_email.split("\t", 1)[1]
		assert _ == "", repr(_)
		yield dict(old=old, new=new, email=email, date=date, tz=tz, message=message)


def get_last_rebase_onto(branch_name):
	entries = list(reversed(list(get_reflog_entries(branch_name))))

	for entry in entries:
		if entry["message"].startswith("rebase finished: refs/heads/%s onto " % (branch_name,)):
			return entry["message"].split()[-1]

	return None


class UnknownUpstream(Exception):
	pass


def all_equal(l):
	s = sorted(l)
	if s[0] == s[-1]:
		return True
	return False


def get_upstream_commit(refs):
	"""
	Return the upstream commit that our patches (if we have any) are rebased
	on top of.
	"""
	# Why not get the upstream branch from .git/config and use
	# git rev-list to find the upstream commit, instead of parsing the reflog?
	# Because (1) git rebase allows rebasing onto arbitrary commits, and
	# (2) the user might not have set up an upstream branch

	# TODO: make sure the commit we decide is the upstream commit is actually
	# a parent of the HEAD commit (or ==?)

	# TODO: Uh, how does this work before the user does this first rebase?
	# I'm guessing it doesn't.  Maybe we want to get the upstream branch
	# from .git/config and find the first commit that is part of the upstream branch?

	heads = get_names_on_commit(refs["HEAD"], "heads", refs)
	# More than one head may match our current commit, but not all reflogs
	# will have the rebase information we're looking for.  (e.g. new branch created
	# from another branch will have just "branch: Created from HEAD" in the reflog.)

	# TODO: maybe parse *all* of the reflogs, since any of them could contain
	# the rebase we're looking for (look at the old, new columns)?  That would help
	# in this case: rebase on master, checkout -b another, switch to master,
	# rebase again, checkout another, tagmyrebase.

	if not heads:
		raise UnknownUpstream("HEAD is not on any branches;"
			"we need a branch to read a reflog in .git/logs/refs/heads/")

	upstreams = filter(lambda u: u is not None, map(get_last_rebase_onto, heads))
	if not upstreams:
		raise UnknownUpstream("Could not find a rebase in reflogs for %r" % (heads,))

	if not all_equal(upstreams):
		raise UnknownUpstream("rebases in reflogs for %r point to "
			"different upstream commits: %r" % (heads, upstreams))

	return upstreams[0]


def main():
	parser = argparse.ArgumentParser(
		description="""
	Utility to mark the HEAD with a branch and timestamped tag, and the upstream
	commit (that we're rebased on top of) with another timestamped tag.  All three
	markings are optional.

	This allows you to

	1) easily find an older set of rebased patches
	2) see in tig/gitk which commits you've previously rebased onto.  This is
	   useful for seeing which new commits you might need to review.""",

		epilog="""
	For any of --tag-upstream, --tag-head, and --branch-head, you can use
	{YMDHMS} to insert the current time, or {YMDN} to insert the current date
	with a counter that avoids collision with existing tags.  Note that the {YMDHMS} or
	{YMDN} will not necessarily correspond on the HEAD and upstream commits.
	""")

	parser.add_argument('-u', '--tag-upstream', dest='tag_upstream',
		help="create a tag with this name pointing to the upstream commit")

	parser.add_argument('-t', '--tag-head', dest='tag_head',
		help="create a tag with this name pointing to HEAD")

	parser.add_argument('-b', '--branch-head', dest='branch_head',
		help="force-create a branch with this name pointing to HEAD")

	args = parser.parse_args()

	if not (args.tag_head or args.branch_head or args.tag_upstream):
		print >>sys.stderr, "Must specify one or more of --tag-head, " \
			"--branch-head, or --tag-upstream; see --help"
		sys.exit(1)

	t = datetime.datetime.now()
	refs = get_refs()

	if args.tag_head or args.tag_upstream:
		upstream_commit = get_upstream_commit(refs)

	if args.tag_upstream:
		existing_tags_on_upstream = get_names_on_commit(upstream_commit, "tags", refs)
		if any(get_re_for_format_string(args.tag_upstream).match(tag) \
			for tag in existing_tags_on_upstream):
			print "Already tagged with %r: %s %s" % (
				existing_tags_on_upstream,
				upstream_commit,
				get_commit_message(upstream_commit))
		else:
			expanded_tag_upstream = get_expanded_name(args.tag_upstream, t, refs)
			subprocess.check_call(["git", "tag", "-a", "--message", "",
				expanded_tag_upstream, upstream_commit])
			print "Created: %s -> %s %s" % (
				expanded_tag_upstream,
				upstream_commit,
				get_commit_message(upstream_commit))

	if args.tag_head:
		existing_tags_on_head = get_names_on_commit(refs["HEAD"], "tags", refs)
		if any(get_re_for_format_string(args.tag_head).match(tag) \
			for tag in existing_tags_on_head):
			print "Already tagged with %r: %s %s" % (
				existing_tags_on_head,
				refs["HEAD"],
				get_commit_message(refs["HEAD"]))
		else:
			expanded_tag_head = get_expanded_name(args.tag_head, t, refs)
			subprocess.check_call(["git", "tag", "-a", "--message",
				make_tag_message(upstream_commit),
				expanded_tag_head])
			print "Created: %s -> %s %s" % (
				expanded_tag_head,
				refs["HEAD"],
				get_commit_message(refs["HEAD"]))

	if args.branch_head:
		branch_name = get_expanded_name(args.branch_head, t, refs)
		if refs["heads"].get(branch_name) == refs["HEAD"]:
			print "Already branched as %s: %s %s" % (
				branch_name,
				refs["HEAD"],
				get_commit_message(refs["HEAD"]))
		else:
			subprocess.check_call(["git", "branch", "-f", branch_name])
			print "Created: %s -> %s %s" % (
				branch_name,
				refs["HEAD"],
				get_commit_message(refs["HEAD"]))


if __name__ == '__main__':
	main()
