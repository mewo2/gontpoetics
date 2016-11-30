all: book.pdf

book.pdf: book/book.tex book/poems.tex
	latexmk -pdf book/book

book/poems.tex:
	python3 generate.py 500

clean:
	rm -f book.* book/*.pdf book/poems.*

count: book/poems.tex book/book.tex
	texcount -1 -inc -sum book/book.tex
