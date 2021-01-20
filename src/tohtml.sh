cd ~/git/nbconvert-blog-template/
jupyter nbconvert ~/git/sme_god-components/statistics.ipynb \
    --to html --output-dir ~/git/sme_god-components_gh-pages \
    --output index.html \
    --template blog
cd ~/git/sme_god-components_gh-pages
git add .
git commit -m "Update web version of Notebook at $( date +%T )"
git push