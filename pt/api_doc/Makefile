.PHONY: all clean
all:
	docker run -v $(shell pwd):/tmp -t aglio -i /tmp/api.apib -o /tmp/api.html
	perl -i -pe 's/>OPTIONS</>SOCKET</g' api.html
	perl -i -pe 's|/socket/association|/socket|g' api.html
	perl -i -pe 's|/socket/bids|/socket|g' api.html
	perl -i -pe 's|/socket/history|/socket|g' api.html
	open api.html
