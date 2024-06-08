import requests
from bs4 import BeautifulSoup
from random import choice
import time
import pandas as pd

@st.cache_data(show_spinner=False)
def scrape_quotes():
    all_quotes = []
    base_url = "http://quotes.toscrape.com/"
    url = "/page/1"
    
    while url:
        res = requests.get(f"{base_url}{url}")
        soup = BeautifulSoup(res.text, "html.parser")
        quotes = soup.find_all(class_="quote")
        
        for quote in quotes:
            all_quotes.append({
                "text": quote.find(class_="text").get_text(),
                "author": quote.find(class_="author").get_text(),
                "bio-link": quote.find("a")["href"]
            })
        next_btn = soup.find(class_="next")
        url = next_btn.find("a")["href"] if next_btn else None

    # Save the data to CSV file
    pd.DataFrame(all_quotes).to_csv('quotes.csv', index=False)
    
    return all_quotes

def initialize_state():
    if 'quote' not in st.session_state:
        st.session_state.quote = choice(st.session_state.all_quotes)
    if 'remaining_guesses' not in st.session_state:
        st.session_state.remaining_guesses = 4
    if 'guess' not in st.session_state:
        st.session_state.guess = ''
    if 'hint' not in st.session_state:
        st.session_state.hint = ''
    if 'answer_revealed' not in st.session_state:
        st.session_state.answer_revealed = False
    if 'countdown' not in st.session_state:
        st.session_state.countdown = 5

def reset_game():
    st.session_state.quote = choice(st.session_state.all_quotes)
    st.session_state.remaining_guesses = 4
    st.session_state.guess = ''
    st.session_state.hint = ''
    st.session_state.answer_revealed = False
    st.session_state.countdown = 5

def main():
    st.title("**Quote Guessing Game**")

    if 'all_quotes' not in st.session_state:
        st.session_state.all_quotes = scrape_quotes()
    
    initialize_state()

    st.write("Here's a quote: ")
    st.write(f"*{st.session_state.quote['text']}*")

    if not st.session_state.answer_revealed:
        guess = st.text_input(f"Who said this quote? Guesses remaining {st.session_state.remaining_guesses}")

        if st.button("Submit Guess"):
            if guess.lower() == st.session_state.quote["author"].lower():
                st.success("CONGRATULATIONS!!! YOU GOT IT RIGHT")
                st.session_state.answer_revealed = True
            else:
                st.session_state.remaining_guesses -= 1
                st.session_state.guess = guess

                if st.session_state.remaining_guesses == 3:
                    res = requests.get(f"http://quotes.toscrape.com{st.session_state.quote['bio-link']}")
                    soup = BeautifulSoup(res.text, "html.parser")
                    birth_date = soup.find(class_="author-born-date").get_text()
                    birth_place = soup.find(class_="author-born-location").get_text()
                    st.session_state.hint = f"Hint: The author was born on {birth_date} {birth_place}"
                
                elif st.session_state.remaining_guesses == 2:
                    st.session_state.hint = f"Hint: The author's first name starts with: {st.session_state.quote['author'][0]}"
                
                elif st.session_state.remaining_guesses == 1:
                    last_initial = st.session_state.quote["author"].split(" ")[1][0]
                    st.session_state.hint = f"Hint: The author's last name starts with: {last_initial}"
                
                elif st.session_state.remaining_guesses == 0:
                    st.session_state.hint = f"Sorry, you ran out of guesses. The answer was {st.session_state.quote['author']}"
                    st.session_state.answer_revealed = True

        if st.session_state.hint and st.session_state.remaining_guesses > 0:
            st.write(st.session_state.hint)
    else:
        st.write(f"The answer was: {st.session_state.quote['author']}")
        st.write("Next quote in:")
        countdown_placeholder = st.empty()
        for i in range(st.session_state.countdown, 0, -1):
            countdown_placeholder.write(f"{i} seconds")
            time.sleep(1)
        reset_game()
        st.experimental_rerun()

if __name__ == "__main__":
    main()