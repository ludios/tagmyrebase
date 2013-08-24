get_last_of_two_rebases = """\
dbbbc27428df5781abc6bb645f8f9e1c6de95ac8 31af98bb0cf13efb15356f3a2d2d19b741354325 Ivan Kozik <ivan@ludios.org> 1377313727 +0000 checkout: moving from master to 31af98bb0cf13efb15356f3a2d2d19b741354325^0
31af98bb0cf13efb15356f3a2d2d19b741354325 9bac0f3cc068b7b7ae5e88261d5b33de067960fa Ivan Kozik <ivan@ludios.org> 1377313728 +0000 rebase: Add mything
9bac0f3cc068b7b7ae5e88261d5b33de067960fa 1ef55318f0320c112f08645434264ce73d0d8e7f Ivan Kozik <ivan@ludios.org> 1377313728 +0000 rebase: Work more on mything
1ef55318f0320c112f08645434264ce73d0d8e7f e026fef9f062741e3dc737f7b253b270b076125d Ivan Kozik <ivan@ludios.org> 1377313729 +0000 rebase: Work on blah
e026fef9f062741e3dc737f7b253b270b076125d e026fef9f062741e3dc737f7b253b270b076125d Ivan Kozik <ivan@ludios.org> 1377313729 +0000 rebase finished: returning to refs/heads/master
e026fef9f062741e3dc737f7b253b270b076125d 227706eb20d70be99fa357b0e62084df7aaf35b7 Ivan Kozik <ivan@ludios.org> 1377313856 +0000 checkout: moving from master to 227706eb20d70be99fa357b0e62084df7aaf35b7^0
227706eb20d70be99fa357b0e62084df7aaf35b7 b0b34a580b6b867e7cbcc8951747dcf1f2970b9d Ivan Kozik <ivan@ludios.org> 1377313856 +0000 pull -v --rebase: Add mything
b0b34a580b6b867e7cbcc8951747dcf1f2970b9d 2834449ed01b2009d6964ad012561785a045795f Ivan Kozik <ivan@ludios.org> 1377313857 +0000 pull -v --rebase: Work more on mything
2834449ed01b2009d6964ad012561785a045795f d826ca4a066020a297f50068d46a4a1affbd2f35 Ivan Kozik <ivan@ludios.org> 1377313857 +0000 pull -v --rebase: Work on blah
d826ca4a066020a297f50068d46a4a1affbd2f35 d826ca4a066020a297f50068d46a4a1affbd2f35 Ivan Kozik <ivan@ludios.org> 1377313857 +0000 rebase finished: returning to refs/heads/master
"""
# expect 227706eb20d70be99fa357b0e62084df7aaf35b7


unfinished_rebase = """\
d826ca4a066020a297f50068d46a4a1affbd2f35 2d7300ecbf92781e67ecc1ccd68c1b71c56d4bca Ivan Kozik <ivan@ludios.org> 1377315076 +0000 checkout: moving from master to 2d7300ecbf92781e67ecc1ccd68c1b71c56d4bca^0
2d7300ecbf92781e67ecc1ccd68c1b71c56d4bca b2c827e63cd237fe0a4b6d339880146559a6531f Ivan Kozik <ivan@ludios.org> 1377315077 +0000 pull -r: Add mything
b2c827e63cd237fe0a4b6d339880146559a6531f 437eff411d2e5a5cb670ad16cd7cff8f11d8f320 Ivan Kozik <ivan@ludios.org> 1377315077 +0000 pull -r: Work more on mything
"""
# expect None or some kind of failure about an unfinished rebase

rebase_followed_by_aborted_rebase = """\
e026fef9f062741e3dc737f7b253b270b076125d 227706eb20d70be99fa357b0e62084df7aaf35b7 Ivan Kozik <ivan@ludios.org> 1377313856 +0000 checkout: moving from master to 227706eb20d70be99fa357b0e62084df7aaf35b7^0
227706eb20d70be99fa357b0e62084df7aaf35b7 b0b34a580b6b867e7cbcc8951747dcf1f2970b9d Ivan Kozik <ivan@ludios.org> 1377313856 +0000 pull -v --rebase: Add mything
b0b34a580b6b867e7cbcc8951747dcf1f2970b9d 2834449ed01b2009d6964ad012561785a045795f Ivan Kozik <ivan@ludios.org> 1377313857 +0000 pull -v --rebase: Work more on mything
2834449ed01b2009d6964ad012561785a045795f d826ca4a066020a297f50068d46a4a1affbd2f35 Ivan Kozik <ivan@ludios.org> 1377313857 +0000 pull -v --rebase: Work on blah
d826ca4a066020a297f50068d46a4a1affbd2f35 d826ca4a066020a297f50068d46a4a1affbd2f35 Ivan Kozik <ivan@ludios.org> 1377313857 +0000 rebase finished: returning to refs/heads/master
d826ca4a066020a297f50068d46a4a1affbd2f35 2d7300ecbf92781e67ecc1ccd68c1b71c56d4bca Ivan Kozik <ivan@ludios.org> 1377315076 +0000 checkout: moving from master to 2d7300ecbf92781e67ecc1ccd68c1b71c56d4bca^0
2d7300ecbf92781e67ecc1ccd68c1b71c56d4bca b2c827e63cd237fe0a4b6d339880146559a6531f Ivan Kozik <ivan@ludios.org> 1377315077 +0000 pull -r: Add mything
b2c827e63cd237fe0a4b6d339880146559a6531f 437eff411d2e5a5cb670ad16cd7cff8f11d8f320 Ivan Kozik <ivan@ludios.org> 1377315077 +0000 pull -r: Work more on mything
437eff411d2e5a5cb670ad16cd7cff8f11d8f320 d826ca4a066020a297f50068d46a4a1affbd2f35 Ivan Kozik <ivan@ludios.org> 1377315158 +0000 rebase: aborting
"""
# expect 227706eb20d70be99fa357b0e62084df7aaf35b7

