"""
Τεχνολογία Λογισμικού: Παραδοτέο 4
1386 ΣΑΝΙΔΑ
1775 ΚΑΖΑΣ
1776 ΑΓΑΘΑΓΓΕΛΙΔΟΥ
1777 ΑΪΣΟΠΟΥΛΟΣ
--------------------------------
E-Commerce Scraper
"""

import requests
from bs4 import BeautifulSoup
import random
import datetime

class Product:
    def __init__(self, name, price, location=""):
        self.name = name
        self.price = price
        self.location = location

    @staticmethod
    def average_price(products):
        total = sum(product.price for product in products)
        return total / len(products)

    @staticmethod
    def highest_price(products):
        return max(products, key=lambda product: product.price)

    @staticmethod
    def lowest_price(products):
        return min(products, key=lambda product: product.price)


class PriceTracker:
    def __init__(self):
        self.price_history = {}

    def track_prices(self, product):
        if product.name not in self.price_history:
            self.price_history[product.name] = []
        self.price_history[product.name].append((product.price, datetime.datetime.now()))


class Database:
    def __init__(self):
        self.products = []

    def save(self, product):
        self.products.append(product)

    def load(self):
        return self.products

    def clear(self):
        self.products = []


class Filter:
    @staticmethod
    def filter_by_price(products, min_price, max_price):
        return [product for product in products if min_price <= product.price <= max_price]

    @staticmethod
    def filter_by_location(products, location):
        return [product for product in products if product.location == location]


class Comparison:
    @staticmethod
    def compare_prices(product1, product2):
        return product1.price - product2.price


class User:
    def __init__(self, username):
        self.username = username
        self.logged_in = False

    def login(self):
        self.logged_in = True
        print(f"{self.username} logged in.")

    def logout(self):
        self.logged_in = False
        print(f"{self.username} logged out.")


class Display:
    @staticmethod
    def show_average_price(products):
        avg_price = Product.average_price(products)
        print(f"Average Price: ${avg_price:.2f}")

    @staticmethod
    def show_highest_price(products):
        highest = Product.highest_price(products)
        print(f"Highest Price: {highest.name} at ${highest.price:.2f}")

    @staticmethod
    def show_lowest_price(products):
        lowest = Product.lowest_price(products)
        print(f"Lowest Price: {lowest.name} at ${lowest.price:.2f}")

    @staticmethod
    def show_closest_location(products, user_location):
        # Filter out products without location
        products_with_location = [product for product in products if product.location]
        if not products_with_location:
            print("No products with location information.")
            return
        closest = min(products_with_location, key=lambda product: abs(ord(product.location[0]) - ord(user_location[0])))
        print(f"Closest Product: {closest.name} in {closest.location}")


class Scraper:
    def __init__(self):
        self.database = Database()

    def scrape_car_gr(self, search_query):
        url = f'https://www.car.gr/search/{search_query}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        for listing in soup.select('.vehicle-listing'):
            name = listing.select_one('.vehicle-title').text.strip()
            price = float(listing.select_one('.vehicle-price').text.strip().replace('€', '').replace(',', ''))
            location = listing.select_one('.vehicle-location').text.strip()
            product = Product(name, price, location)
            self.database.save(product)

    def scrape_skroutz_gr(self, search_query):
        url = f'https://www.skroutz.gr/search/{search_query}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        for listing in soup.select('.product-item'):
            name = listing.select_one('.product-title').text.strip()
            price = float(listing.select_one('.product-price').text.strip().replace('€', '').replace(',', ''))
            product = Product(name, price)
            self.database.save(product)

    def scrape_ebay_com(self, search_query):
        url = f'https://www.ebay.com/sch/i.html?_nkw={search_query}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        for listing in soup.select('.s-item'):
            name = listing.select_one('.s-item__title').text.strip()
            price_text = listing.select_one('.s-item__price').text.strip()
            
            # Remove any non-numeric characters (e.g., currency symbols)
            price_text = ''.join(c for c in price_text if (c.isdigit() or c == '.'))
            if price_text:
                try:
                    price = float(price_text)
                    product = Product(name, price)
                    self.database.save(product)
                except ValueError:
                    continue

    def scrape(self, search_query):
        self.database.clear()
        self.scrape_car_gr(search_query)
        self.scrape_skroutz_gr(search_query)
        self.scrape_ebay_com(search_query)
        print("\n> Scraping complete. Products saved to database. <")

    def get_products(self):
        return self.database.load()


def main():
    scraper = Scraper()
    user = User("newUser")
    user.login()

    search_query = input("Enter the product you want to search for: ")
    scraper.scrape(search_query)

    products = scraper.get_products()

    if not products:
        print("> No products found. <")
        return

    while True:
        print("\nFilter options:")
        print("1. Show highest price")
        print("2. Show lowest price")
        print("3. Show closest location")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            Display.show_highest_price(products)
        elif choice == "2":
            Display.show_lowest_price(products)
        elif choice == "3":
            user_location = input("Enter your location: ")
            Display.show_closest_location(products, user_location)
        elif choice == "4":
            break
        else:
            print("----Invalid choice, please try again.-----")

    user.logout()


if __name__ == "__main__":
    main()
