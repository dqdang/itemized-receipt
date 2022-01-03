import argparse
from bs4 import BeautifulSoup
import json
import os
import requests
import sys

import tkinter as tk
from tkinter import *


def scrape_websites():
    '''
    scrape_websites
    scrapes the websites from the base_URL
    '''
    all_build_sites = []
    all_items = {}
    base_URL = "https://www.icy-veins.com/d3/"
    r = requests.get(base_URL)
    soup_of_all = BeautifulSoup(r.content, "html.parser")
    build_links = soup_of_all.select(
        "div.nav_content_block_d3_build > span > a")
    for link in build_links:
        str_link = str(link).lower()
        if "with" in str_link:
            all_build_sites.append("http:" + link['href'])
    for build_site in all_build_sites:
        r = requests.get(build_site)
        soup_of_build = BeautifulSoup(r.content, "html.parser")
        list_of_items_for_build = soup_of_build.select("span.d3_icon_span > a")
        for item in list_of_items_for_build:
            if item.text not in all_items:
                all_items[item.text] = [build_site]
            else:
                all_items[item.text].append(build_site)

    initialize_db(all_items)


def initialize_db(items):
    '''
    initialize_db
    initializes the database
    '''
    cur_path = os.path.dirname(os.path.abspath(__file__))
    f_name = os.path.join(cur_path, "icy_n_veiny.json")
    with open(f_name, "w") as f:
        json.dump(items, f, sort_keys=True)


def read_from_db():
    '''
    reads_from_file
    load the database
    '''
    cur_path = os.path.dirname(os.path.abspath(__file__))
    f_name = os.path.join(cur_path, "icy_n_veiny.json")
    with open(f_name, "r") as f:
        items = json.load(f)
    return items


def partial_search(item, list_of_items):
    '''
    partial_search
    partial search in database
    '''

    search_results = []
    item = item.lower().strip()
    for each_item in list_of_items:
        orig = each_item
        each_item = each_item.lower()
        if each_item.startswith(item):
            search_results.append(orig)
    return search_results


def check_for_item(item, list_of_items):
    '''
    check_for_item
    checks the database if the item is in it
    '''
    results = partial_search(item, list_of_items)
    if len(results) > 0:
        b_string = ""
        for each_item in results:
            b_string += "{}\n".format(each_item)
            for build_link in list_of_items[each_item]:
                b_string += "{}\n".format(build_link)
        text.delete(1.0, END)
        text.insert(END, "Item in build:\n{}".format(b_string))
        text.pack()
    else:
        text.delete(1.0, END)
        text.insert(END, "Item not in build. Can scrap.")
        text.pack()


def arg_parser():
    '''
    arg_parser
    argument parser for command line
    '''
    parser = argparse.ArgumentParser(
        description="icy-veins: scraper for icy-veins")

    parser.add_argument("-s", "--scrape", dest="scrape", action="store_true",
                        help="scrape from icy-veins website to rebuild local database")

    return parser


def main():
    '''
    main
    main function
    '''
    parser = arg_parser()
    args = parser.parse_args()
    if args.scrape:
        scrape_websites()


if __name__ == "__main__":
    main()
    root = tk.Tk()
    width = 500
    height = 500
    root.geometry("{}x{}".format(width, height))
    top = Frame(root)
    top.config(bg="black")
    top.pack(side=TOP)

    bottom = Frame(root)
    bottom.config(bg="black")
    bottom.pack(side=BOTTOM)

    frame = Frame(root)
    frame.pack()

    item = tk.Entry(top)
    item.grid(row=0, column=1)
    # item.pack()

    root.title("Diablo Items in Icy Veins")
    root.config(bg="black")

    tk.Label(top, text="Item: ").grid(row=0, column=0)
    text = tk.Text(root)
    text.configure(bg=root.cget('bg'), foreground="white", relief="flat")
    list_of_items = read_from_db()
    button = tk.Button(bottom,
                       text='Search', command=lambda: check_for_item(item.get(), list_of_items)).grid(row=0, column=0)
    # button.pack()
    root.bind('<Return>', lambda event=None: check_for_item(
        item.get(), list_of_items))
    quit = Button(bottom, text="Quit", command=root.quit).grid(row=0, column=1)
    # quit.pack()
    tk.mainloop()
