REGISTERED_COMPONENTS = []

class BaseComponent:
    def register(self):
        REGISTERED_COMPONENTS.append(self)

class Heading(BaseComponent):
    """Creates a full-width section header. Example: Heading("Contact") or Heading("shreyash@swami", CurrentDate())"""
    def __init__(self, title, right_text=None):
        self.type = "heading"
        self.title = title
        self.right_text = right_text
        self.register()

class CurrentDate:
    """Dynamically injects the current date string."""
    def __init__(self):
        self.type = "current_date"

class Value(BaseComponent):
    """Creates a key-value pair line. Example: Value("OS", "Linux")"""
    def __init__(self, key, value):
        self.type = "value"
        self.key = key
        self.value = value
        self.register()

class TimeElapsed(BaseComponent):
    """Calculates and displays years, months, and days since a specific date. Example: TimeElapsed("Uptime", 2004, 12, 7)"""
    def __init__(self, key, year, month, day):
        self.type = "time_elapsed"
        self.key = key
        self.year = year
        self.month = month
        self.day = day
        self.register()

class Separator(BaseComponent):
    """Creates an empty dotted separator line to space things out."""
    def __init__(self):
        self.type = "separator"
        self.register()
        
class WorkingOn(BaseComponent):
    """Automatically shows what repository you are currently working on based on recent pushes."""
    def __init__(self):
        self.type = "working_on"
        self.register()

class CommitGraph(BaseComponent):
    """Shows the 28-day sparkline commit graph. Simply add it to the layout to enable."""
    def __init__(self):
        self.type = "commit_graph"
        self.register()

class GithubStats(BaseComponent):
    """
    Shows a two-column layout for GitHub stats.
    Valid options are: "Repos", "Stars", "Commits", "Followers", "Pull.Requests", "Lines.of.Code".
    Example: GithubStats("Repos", "Commits")
    """
    def __init__(self, *args):
        self.type = "github_stats"
        self.stats = args
        self.register()

class Last24Hr(BaseComponent):
    """
    Shows an activity feed of your last 24 hours.
    Valid options are: "Pushes", "Pull.Requests", "Issues", "Starred", "Forked", "Releases", "Reviewed", "Comments".
    Example: Last24Hr("Pushes", "Pull.Requests")
    """
    def __init__(self, *args):
        self.type = "last_24_hr"
        self.events = args
        self.register()
