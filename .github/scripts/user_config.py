from components import Heading, Value, TimeElapsed, Separator, WorkingOn, CommitGraph, GithubStats, Last24Hr, CurrentDate
"""
=====================================================================
GITHUB TOKEN INSTRUCTIONS
=====================================================================
To use this script, you need a GitHub Personal Access Token (PAT).
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" (classic).
3. Give it a name, expiration, and check the "repo" and "user" scopes.
4. Copy the generated token.
5. Go to your repository settings -> Secrets and variables -> Actions.
6. Click "New repository secret".
7. Name it "GITHUB_TOKEN" and paste your token in the secret field.
=====================================================================
"""
# 1. General Info (Required for Github Stats)
GITHUB_USERNAME = "Shreyash0712"

# 2. Terminal Layout
# You can easily add, remove, or modify the structure of your profile using these components.
# Check out components.py to understand what components are available and possible arguments for each. 
TERMINAL_SECTIONS = [
    Heading("Shreyash@Swami", CurrentDate()),
    Value("OS", "Windows 11, Linux (Fedora)"),
    TimeElapsed("Uptime", 2004, 12, 7),
    Value("IDE", "VSCode, Antigravity, IntelliJ"),
    Value("Status", "Open For Work"),
    Separator(),
    Separator(),
    Value("Languages.Programming", "JavaScript, Java, Python"),
    Value("Languages.Real", "English, Hindi"),
    Separator(),
    Value("Hobbies.Software", "Web-Dev, AI, Cloud"),
    Value("Hobbies.Hardware", "Table-Tennis, Reading"),
    Separator(),
    Heading("Contact"),
    Value("Email", "shreyash.swami2476@gmail.com"),
    Value("LinkedIn", "in/shreyashswami"),
    Separator(),
    GithubStats("Repos", "Stars", "Commits", "Followers", "Pull.Requests", "Lines.of.Code"),
    Separator(),
    CommitGraph(),
    Last24Hr("Pushes", "Pull.Requests", "Issues", "Forked", "Releases", "Reviewed", "Comments")
]
