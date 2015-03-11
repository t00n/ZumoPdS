.PHONY: all run

all: pack.tar.gz.uploaded
run: all
	ssh root@Robot.local 'rm -f pack.tar && gunzip pack.tar.gz && tar xf pack.tar && python repl.py carre.logo'

pack.tar.gz: logo.py repl.py zumoturtle.py carre.logo
	tar c $^ | gzip > $@

%.uploaded: %
	scp $< root@Robot.local: && touch $@
