all: carre.logo.uploaded logo.py.uploaded zumoturtle.py.uploaded

%.uploaded: %
	scp $< root@Robot.local: && touch $@

run: all
	ssh root@Robot.local 'python logo.py carre.logo'
