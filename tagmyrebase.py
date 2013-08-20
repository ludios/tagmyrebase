"""
(Draft)

Operations:

mb - mark current commit as bien, mark detected upstream commit as gu
	Creates a git tag that contains the current date and the upstream commit
mu - mark this commit as a known-good upstream commit
	Creates a git tag with the current date
		Does not include the upstream branch name; branch names can change
lsb - list bien commits
	You can use this to jump to an older bien, which may have different
	patches than the ones you have on the latest bien
lsu - list upstream commits
	Note that marked upstream commits may be on different upstream branches
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
	If HEAD matches upstream commit (we have no patches on top of upstream):

	1ca58dc4f6b00660bc82385f5b0d0c05d01881e5 e97eaa20eb92dc4b7c8f481a705c74db80064077 Ivan Kozik <ivan@ludios.org> 1376986238 +0000 checkout: moving from master to e97eaa20eb92dc4b7c8f481a705c74db80064077^0
e97eaa20eb92dc4b7c8f481a705c74db80064077 e97eaa20eb92dc4b7c8f481a705c74db80064077 Ivan Kozik <ivan@ludios.org> 1376986238 +0000 rebase finished: returning to refs/heads/master

	If HEAD does not match upstream commit (we do have patches on top of upstream):

	b06c798443651975c7f1cf381074dad0767e86e1 bcbc9df714ea4a9c835faac3b7776b882a31971e Ivan Kozik <ivan@ludios.org> 1376986783 +0000 checkout: moving from master to bcbc9df714ea4a9c835faac3b7776b882a31971e^0
bcbc9df714ea4a9c835faac3b7776b882a31971e 1e1395dc1a28bc917cc46cb86acf1ba7cb87bd4f Ivan Kozik <ivan@ludios.org> 1376986783 +0000 pull --rebase: Add mything
1e1395dc1a28bc917cc46cb86acf1ba7cb87bd4f 1e1395dc1a28bc917cc46cb86acf1ba7cb87bd4f Ivan Kozik <ivan@ludios.org> 1376986783 +0000 rebase finished: returning to refs/heads/master
	"""
	entries = list(reversed(list(get_reflog_entries("HEAD"))))

	for entry in entries:
		# TODO: add more verification that the rebase finished?
		if entry["message"].startswith("checkout: moving from "):
			return entry["new"]

	raise RuntimeError("Could not find upstream commit in reflog; entries are:\n%s" % (pprint.pformat(entries),))


def get_commit(branch_name):
	return subprocess.check_output(["git", "rev-parse", branch_name]).split()[0]


def now():
	return datetime.datetime.now()


def main():
	parser = argparse.ArgumentParser(description="""
	TODO XXX
	""")

	parser.add_argument('-m', '--mark', dest='mark',
		help="mark the current HEAD with this branch name, and also "
		     "create a tag with this branch name and the current timestamp")

	args = parser.parse_args()

	if args.mark:
		branch_name = args.mark
		if get_commit(branch_name) == get_commit("HEAD"):
			print >>sys.stderr, "HEAD is already marked as %s" % (branch_name,)
		else:
			upstream_commit = get_upstream_commit()
			t = now()
			call(["git", "branch", "-f", branch_name])
			# Mark the upstream commit
			call(["git", "tag", "-a", "--message", "", "upstream-" + get_tag_name(branch_name, t), upstream_commit])
			# Mark the downstream commit
			call(["git", "tag", "-a", "--message", get_tag_message(upstream_commit), get_tag_name(branch_name, t)])
	else:
		print >>sys.stderr, "Must specify --mark branchname"


if __name__ == '__main__':
	main()
