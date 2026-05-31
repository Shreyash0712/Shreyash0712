class Heading:
    """Creates a full-width section header. Example: Heading("Contact") or Heading("shreyash@swami", CurrentDate())"""
    def __init__(self, title, right_text=None):
        self.type = "heading"
        self.title = title
        self.right_text = right_text

class CurrentDate:
    """Dynamically injects the current date string."""
    def __init__(self):
        self.type = "current_date"

class Value:
    """Creates a key-value pair line. Example: Value("OS", "Linux")"""
    def __init__(self, key, value):
        self.type = "value"
        self.key = key
        self.value = value

class TimeElapsed:
    """Calculates and displays years, months, and days since a specific date. Example: TimeElapsed("Uptime", 2004, 12, 7)"""
    def __init__(self, key, year, month, day):
        self.type = "time_elapsed"
        self.key = key
        self.year = year
        self.month = month
        self.day = day

class Separator:
    """Creates an empty dotted separator line to space things out."""
    def __init__(self):
        self.type = "separator"
        
class WorkingOn:
    """Automatically shows what repository you are currently working on based on recent pushes."""
    def __init__(self):
        self.type = "working_on"

class CommitGraph:
    """Shows the 28-day sparkline commit graph. Simply add it to the layout to enable."""
    def __init__(self):
        self.type = "commit_graph"

class GithubStats:
    """
    Shows a two-column layout for GitHub stats.
    Valid options are: "Repos", "Stars", "Commits", "Followers", "Pull.Requests", "Lines.of.Code".
    Example: GithubStats("Repos", "Commits")
    """
    def __init__(self, *args):
        self.type = "github_stats"
        self.stats = args

class Last24Hr:
    """
    Shows an activity feed of your last 24 hours.
    Valid options are: "Pushes", "Pull.Requests", "Issues", "Starred", "Forked", "Releases", "Reviewed", "Comments".
    Example: Last24Hr("Pushes", "Pull.Requests")
    """
    def __init__(self, *args):
        self.type = "last_24_hr"
        self.events = args
