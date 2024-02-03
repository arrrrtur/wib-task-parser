import csv
import bs4
import requests


def fetch_html(url, session):
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML: {e}")
        return None


def parse_html(reviews_data, html, is_checked, pages_count):
    soup = bs4.BeautifulSoup(html, 'html.parser')

    if not is_checked:
        pages_count = soup.find(
            'div', {'class': 'navigator'}
        ).find(
            'ul', {'class': 'list'}
        ).find_all(
            'li', {'class': 'arr'}
        )[-1].find(
            'a', {'href': True}
        )['href'].split('/')[-2]
        is_checked = True

    reviews = soup.find_all('div', {'class': 'reviewItem'})
    for review in reviews:
        review_id = review.find('div', {'id': True})['id']
        author_id = review.find('a', {'href': True, 'itemprop': 'name'})['href'].split('/')[-2]
        author_name = review.find('p', {'class': 'profile_name'}).text.strip()
        title = review.find('p', {'class': 'sub_title'}).text.strip()
        text = review.find('span', {'class': '_reachbanner_'}).text.strip()
        date = review.find('span', {'class': 'date'}).text.strip()
        review_type = review.find('div', {'class': 'response'}).get('class')[1]

        review_data = {
            'review_id': review_id,
            'author_id': author_id,
            'author_name': author_name,
            'title': title,
            'text': text,
            'date': date,
            'review_type': review_type
        }

        reviews_data.append(review_data)

    return [reviews_data, is_checked, int(pages_count)]


def write_to_csv(reviews):
    if not reviews:
        print("No data to write.")
        return

    headers = reviews[0].keys()

    with open('reviews.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(reviews)


def main():
    base_url = "https://www.kinopoisk.ru/film/326/reviews/ord/date/status/all/perpage/200/page/"

    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/121.0.0.0 Safari/537.36",
    })

    reviews = list()
    is_checked = False
    pages_count = 1_000_000_000_000
    page = 1

    while page <= pages_count:
        html = fetch_html(base_url + str(page) + "/", s)
        reviews, is_checked, pages_count = parse_html(reviews, html, is_checked, pages_count)
        page += 1

    write_to_csv(reviews)


if __name__ == "__main__":
    main()
