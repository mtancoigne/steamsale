#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author Manuel Tancoigne
A script that search for the most wanted games (wishlist) of a steam user's friend

Work based on the script of Martin Polden (https://github.com/martinp/steamsale)

@todo : use the script for a given group id (fetch the members)
@todo : use the script on a given text list of users
@todo : integrate the original script by Martin Polden to display discounts on items

"""

import sys
import requests
import re
from re import search
from getopt import getopt, GetoptError
from BeautifulSoup import BeautifulSoup

class Wishlist(object):
    """ Class representing a Steam wishlist """
    def __init__(self, steam_id, steam_username=None):
        if steam_id.isdigit():
            url = 'http://steamcommunity.com/profiles/%s/wishlist' % steam_id
        else:
            url = 'http://steamcommunity.com/id/%s/wishlist' % steam_id
        req = requests.get(url)
        self.soup = BeautifulSoup(req.content, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.tag = None
        self.items = []
        self.steam_id=steam_id
        self.steam_username=steam_username

    def _find_url(self):
        """ Returns game URL or None """
        url = self.tag.find(attrs={'class': re.compile('btn_visit_store')})
        return url.attrMap['href'] if url and 'href' in url.attrMap else "#"

    def find_items(self, only_sale=False, percent_off=0):
        """ Parse and find wishlist items """
        # Find divs containing wishlist items
        item_tags = self.soup.findAll(attrs={'class': "wishlistRowItem\t"})
        for item_tag in item_tags:
            self.tag = item_tag.find(attrs={'class': 'gameListPriceData'})
            title = item_tag.find('h4').text
            url = self._find_url()
            app_id = search(r'\d+/?$', url).group(0)
            self.items.append({'app_id':app_id,'title':title, 'uid':self.steam_id, 'username': self.steam_username})

        return self.items

class Friends(object):
    """ Class representing a Steam friendlist """
    def __init__(self, steam_id):
        if steam_id.isdigit():
            url = 'http://steamcommunity.com/profiles/%s/friends' % steam_id
        else:
            url = 'http://steamcommunity.com/id/%s/friends' % steam_id
        req = requests.get(url)
        self.soup = BeautifulSoup(req.content, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.tag = None
        self.friends = []
        
    def _find_friend_id(self):
        """Returns the Id, digitalized or not """
        url = self.tag.find(attrs={'class': re.compile("linkFriend_(offline|online|in-game)")})
        href = url.attrMap['href'] if url and 'href' in url.attrMap else None
        return search("(.*)/(.*)", href).group(2);
        
    def find_friends(self):
        """ Find divs containing friends blocks """
        friend_tags = self.soup.findAll(attrs={'class' : re.compile("friendBlock_(offline|online|in-game)")})
        for friend_tag in friend_tags:
            self.tag = friend_tag.find('p')
            name = friend_tag.find(attrs={'class': re.compile('linkFriend_(offline|online|in-game)')}).text
            uid= self._find_friend_id()
            self.friends.append({'uid':uid, 'name':name})

        return self.friends

def usage():
    """ Display usage """
    print ('==================================================================')
    print ('This script parses a steam user profile, find friends associated')
    print ('with this user, and their respective wishlists.')
    print ('==================================================================')
    print ('Usage: %s steam_id') % sys.argv[0]
    sys.exit(1)


def main():
    """ Parse argv, find items and print them to stdout """
    try:
        opts, args = getopt(sys.argv[1:],'hdsp:c')
    except GetoptError, err:
        print str(err)
        usage()

    if not args:
        usage()
        
    steam_id = args[0]
    """ First, we search for all friends"""
    print ('Searching for friends...')
    friends = Friends(steam_id)
    friends_list = friends.find_friends()
    wanted_games=[] #List of games wanted by people
    games_list={}   #Dict with more infos on it
    n_games_list={} #List of game_id : wanted count
    print ('--- You have %s friend(s)') % len(friends_list)
    print
    print ('Fetching all of your friends wishlists')


#    i=0
    for (key) in friends_list:
## uncomment this part if you want to test the script on a little set of people
## Also uncomment the i=0 above.
#        if(i<5):
#            wishlist = Wishlist(key['uid'], key['name'])
#            wanted_games.extend(wishlist.find_items())
#            print ('... %s done') % key['name']
#            i=i+1
## comment this part if you want to test the script on a little set of people
        wishlist = Wishlist(key['uid'], key['name'])
        wanted_games.extend(wishlist.find_items())
        print ('... %s done') % key['name']
            
    print ('--- All lists retrieved')
    print
    print ('Doing list stuff :')
    """ Creating game list """
    for (key) in wanted_games:
        if(key['app_id'] in games_list):
            games_list[key['app_id']]['count'] += 1
            games_list[key['app_id']]['users'] += ", " + key['username']
            
        else:
            games_list[key['app_id']]={'game_name':key['title'], 'count':1, 'users':key['username']}
    print ('--- There is %d differents games in the wishlists') % len(games_list)
    print
    
    """ Creating a reference list for games wanted  >= 2 people """
    print ('Deleting one shot games')
    i=0
    for key in games_list:
        if games_list[key]['count']>=2 :
            n_games_list[key]=games_list[key]['count']
        else: i+=1
    print ('--- %d game(s) removed from list') % i
    print
    
    """ Sorting array """
    print ('-------- Results : --------')
    i=len(n_games_list)
    for key, value in sorted(n_games_list.iteritems(), key=lambda (k,v):(v,k)):
        print i,'- score: ', value, '-', games_list[key]['game_name'], '---  Wanted by ', games_list[key]['users']
        i-=1

if __name__ == '__main__':
    main()
