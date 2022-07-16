# DNI

# --- Bot Settings ---
TOKEN = ""
PREFIX = ""

# If you're not using two different bots for testing control, ignore these two lines
PROD_TOKEN = "" 
PROD_PREFIX = ""

LOW_DATA_MODE = False # You can manually set this to True, which will increase cooldown times for certain commands

# --- Wavelink Settings ---
WL_HOST = ""
WL_PORT = 0 
WL_REST_URI = "http://" + WL_HOST + ":" + str(WL_PORT) # Don't change this unless the REST URI is different
WL_PASSWORD = ""

# --- Other Settings ---
PRIVATE_BOT = True
OWNER_ID = 0 # Edit if you're selfhosting
EXTRA_ANNOYING = False # Use at your own discretion

# --- Private Settings ---
# Ignore if PRIVATE_BOT is False
MAIN_CHANNEL = 0
EXTRA_RESPONSES = [] # Add custom responses to pings here

# --- Spotify Settings ---
# Ignore if PRIVATE_BOT is False
SPOTIFY_CLIENT_ID = ""
SPOTIFY_CLIENT_SECRET = ""
PLAYLIST_LINK = ""