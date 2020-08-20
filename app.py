import urllib.request, json
import time
import tweepy
import os





# returns the json albumData from the collection
def readCollection():
    albumData = 0

    # While the album data is 0, continue to loop trying to fetch info from discogs
    while albumData == 0:
        try:
            with urllib.request.urlopen("https://api.discogs.com/users/namedude/collection/folders/0/releases?sort=added&sort_order=desc") as url:
                albumData=json.loads(url.read().decode())

                return albumData
        # If we get an exception from discogs, sleep for a minute to reset        
        except:
            time.sleep(60)





# Tweets the album
def tweet(albumData, api):    
    tweetString = "Just added the album " + albumData['releases'][0]['basic_information']['title'] + " by " + albumData['releases'][0]['basic_information']['artists'][0]['name'] + " to my collection: https://www.discogs.com/user/namedude/collection?sort=added&sort_order=desc"

    if len(tweetString) <= 240:
        api.update_status(tweetString)
    else:
        tweetString = "Just added a " + albumData['releases'][0]['basic_information']['artists'][0]['name'] + " album to my collection: https://www.discogs.com/user/namedude/collection?sort=added&sort_order=desc"
        if len(tweetString) <= 240:
            api.update_status(tweetString)





def tweetMultiple(albumData, amount, api):
    tweetString = "Just added the album " + albumData['releases'][0]['basic_information']['title'] + " by " + albumData['releases'][0]['basic_information']['artists'][0]['name'] + " and " + str(amount - 1) + " other "

    if amount == 2:
        tweetString += "album "
    else:
        tweetString += "albums "    

    tweetString += "to my collection: https://www.discogs.com/user/namedude/collection?sort=added&sort_order=desc"


    if len(tweetString) <= 240:
        api.update_status(tweetString)






def readCollectionSize(albumData):
    return albumData["pagination"]["items"]


def readDateAdded(albumData, index):
    return albumData["releases"][index]["date_added"]



def create_api():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        return -1
    return api



def countRecordsAdded(albumData, lastDate):
    albumsAdded = 0

    # For each record in the collection
    for i in range(0, readCollectionSize(albumData)):
        # Read the date added 
        dateAdded = readDateAdded(albumData, i)

        # If the data added is greater than the last date, add to counter
        if dateAdded > lastDate:
            albumsAdded += 1
        else:
            return albumsAdded



    

def main():
    # Authenticate the API
    api = create_api()      
    if api == -1:
        return -1
     
    # Read the albumData from the latest record in the collection
    albumData = readCollection()

    # We will use date added to check if we need to tweet or not
    lastDate = readDateAdded(albumData, 0)

    while True:
        # Sleep for 15 minutes
        time.sleep(15 * 60)                                                       

        # Check collection
        albumData = readCollection()

        # Read the new date
        newDate = readDateAdded(albumData, 0)

        # If new date is greater than old date, count how many records are greater than new date
        if newDate > lastDate:
            #sleep for 5 minutes to allow a 5 minute window to add records
            time.sleep(5 * 60)

            # Check collection again
            albumData = readCollection()

            # Read the new date again
            newDate = readDateAdded(albumData, 0)

            albumsAdded = countRecordsAdded(albumData, lastDate)

            # Try to tweet about the records
            try:
                # If 1 album was added, tweet about it
                if albumsAdded == 1:
                    tweet(albumData, api)
                # If multiple records were added, tweet about them    
                elif albumsAdded > 1:
                    tweetMultiple(albumData, albumsAdded, api)   
            # Catch duplicate tweet exception        
            except:
                pass
                
            # Set last date to the new date of the records    
            lastDate = newDate     




            
        
if __name__ == "__main__":
    main()