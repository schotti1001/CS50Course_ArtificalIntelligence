import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_pages = {}
    probability_random_page = (1-damping_factor) / len(corpus)

    links = corpus[page]
    if len(links) == 0:
        probability_random_page = 1 / len(corpus)
    else:   #to ensure no division by 0
        probability_following_link = damping_factor / len(links)

    for link in links:
        probability_pages[link] = probability_following_link + probability_random_page
   
    not_linked_pages = []
    for page in corpus:
        if not probability_pages.__contains__(page):
            not_linked_pages.append(page)

    for not_linked_page in not_linked_pages:
        probability_pages[not_linked_page] = probability_random_page
    return probability_pages



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    current_page = random.choice(list(corpus.items()))[0]
    visited_times_per_page = {}
    for i in range(n):
        probabilitys_next =transition_model(corpus, current_page, damping_factor)
        random_nr = random.random()
        current_sum_value = 0
        next_page = None
        for probability in probabilitys_next:
            current_sum_value += probabilitys_next[probability]
            if random_nr < current_sum_value:
                next_page = probability
                break    

        if not visited_times_per_page.__contains__(next_page):    
            visited_times_per_page[next_page] = 0
        visited_times_per_page[next_page] = visited_times_per_page[next_page] + 1
        current_page = next_page
    
    probability_pages = {}
    for page in visited_times_per_page:
        probability_pages[page] = visited_times_per_page[page] / n
    return probability_pages

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probability_pages = {}
    #init
    for page in corpus:
        probability_pages[page] = (1 / len(corpus), 1) #(current, last_change)
    #create dict with links to page
    links_to_page = {}
    for page in corpus:
        links_to_page[page] = []
        for linking_page in corpus:
            if corpus[linking_page].__contains__(page) or len(corpus[linking_page]) == 0:
                links_to_page[page].append(linking_page)

    while check_Continue(probability_pages):
        for page in probability_pages:
            probability_from_page = 0
            for linkin_page in links_to_page[page]:
                link_count = None
                if len(corpus[linkin_page]) == 0:
                    link_count = len(corpus)
                else:
                    link_count = len(corpus[linkin_page])

                probability_from_page += probability_pages[linkin_page][0] / link_count
            new_page_rank = (1 - damping_factor)/len(corpus) + damping_factor * probability_from_page
            change = abs(probability_pages[page][0]- new_page_rank)
            probability_pages[page] = (new_page_rank, change)
    result = {}
    for probabilty in probability_pages:
        result[probabilty] = probability_pages[probabilty][0]
    return result

def check_Continue(probability_pages):
    for page in probability_pages:
        if probability_pages[page][1] > 0.001:
            return True
    return False

if __name__ == "__main__":
    main()
