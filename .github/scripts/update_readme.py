import os
import urllib.request
import json
from datetime import date
import re

def fetch_json(url, token):
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def fetch_graphql(query, token):
    req = urllib.request.Request("https://api.github.com/graphql", method="POST")
    req.add_header("Authorization", f"bearer {token}")
    req.add_header("Content-Type", "application/json")
    data = json.dumps({"query": query}).encode("utf-8")
    with urllib.request.urlopen(req, data=data) as response:
        return json.loads(response.read())

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("No GITHUB_TOKEN provided")
        return
    
    username = "Shreyash0712"
    
    # 1. User Data
    user_data = fetch_json(f"https://api.github.com/users/{username}", token)
    followers = user_data.get("followers", 0)
    public_repos = user_data.get("public_repos", 0)
    
    # 2. Repos (for stars and LOC)
    repos = fetch_json(f"https://api.github.com/users/{username}/repos?per_page=100", token)
    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    
    total_loc = 0
    for repo in repos:
        if not repo.get("fork", False):
            try:
                langs = fetch_json(repo["languages_url"], token)
                total_bytes = sum(langs.values())
                total_loc += total_bytes // 35 
            except Exception:
                pass
            
    # 3. Commits & PRs & Contributed (via GraphQL)
    query = """
    {
      user(login: "%s") {
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
        }
        repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
          totalCount
        }
      }
    }
    """ % username
    
    try:
        gql_data = fetch_graphql(query, token)
        contrib_collection = gql_data["data"]["user"]["contributionsCollection"]
        commits = contrib_collection["totalCommitContributions"]
        prs = contrib_collection["totalPullRequestContributions"]
        contrib = gql_data["data"]["user"]["repositoriesContributedTo"]["totalCount"]
    except Exception as e:
        commits = "N/A"
        prs = "N/A"
        contrib = "N/A"

    # 4. Date and Uptime
    dob = date(2004, 12, 7) 
    today = date.today()
    
    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day
    
    if days < 0:
        months -= 1
        days += 30 
    if months < 0:
        years -= 1
        months += 12
        
    uptime_str = f"{years} years, {months} months, {days} days"
    current_date_str = today.strftime("%B %d, %Y")

    def fmt(n):
        return f"{n:,}" if isinstance(n, int) else str(n)

    # 5. Format Lines Dynamically
    TOTAL_WIDTH = 68

    def pad_line(label, value):
        left = f". {label}: "
        right = f" {value}"
        dots = "." * max(1, (TOTAL_WIDTH - len(left) - len(right)))
        return f"{left}{dots}{right}"

    def pad_double(label1, val1, label2, val2):
        half = (TOTAL_WIDTH - 3) // 2
        left1 = f". {label1}: "
        right1 = f" {val1}"
        dots1 = "." * max(1, half - len(left1) - len(right1))
        p1 = f"{left1}{dots1}{right1}"
        
        left2 = f"{label2}: "
        right2 = f" {val2}"
        rem = TOTAL_WIDTH - len(p1) - 3
        dots2 = "." * max(1, rem - len(left2) - len(right2))
        p2 = f"{left2}{dots2}{right2}"
        return f"{p1} | {p2}"

    def make_header(title):
        base = f"- {title} "
        return base + "-" * max(1, TOTAL_WIDTH - len(base))

    lines = [
        f"shreyash@swami " + "-" * (TOTAL_WIDTH - 15),
        pad_line("OS", "Windows 11, Linux (Fedora)"),
        pad_line("Uptime", uptime_str),
        pad_line("Host", "Homo Sapiens"),
        pad_line("Kernel", "Software Engineer v1.0"),
        pad_line("IDE", "VSCode, Antigravity, IntelliJ"),
        ".",
        pad_line("Languages.Programming", "JavaScript, Java, Python"),
        pad_line("Languages.Real", "English, Hindi"),
        ".",
        pad_line("Hobbies.Software", "Web Dev, AI, Cloud"),
        pad_line("Hobbies.Hardware", "Custom PCs, Keyboards"),
        ".",
        make_header("Contact"),
        pad_line("Email", "shreyash.swami2476@gmail.com"),
        pad_line("LinkedIn", "shreyashswami"),
        ".",
        make_header("GitHub Stats"),
        pad_double("Repos", f"{fmt(public_repos)} [Contrib: {fmt(contrib)}]", "Stars", fmt(stars)),
        pad_double("Commits", fmt(commits), "Followers", fmt(followers)),
        pad_double("Pull Requests", fmt(prs), "Lines of Code", f"~{fmt(total_loc)}"),
        ".",
        make_header("Date"),
        pad_line("Current Date", current_date_str),
    ]

    def generate_svg(theme):
        bg_color = "#0d1117" if theme == "dark" else "#ffffff"
        text_color = "#c9d1d9" if theme == "dark" else "#24292f"
        
        width = 620
        height = 20 * len(lines) + 40
        
        svg = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
            f'<style>',
            f'  .text {{ font-family: "Courier New", Courier, monospace; font-size: 14px; fill: {text_color}; }}',
            f'</style>',
            f'<rect width="{width}" height="{height}" fill="{bg_color}" rx="10" />',
            f'<g class="text">'
        ]
        
        for i, line in enumerate(lines):
            y = 30 + i * 20
            line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            svg.append(f'<text x="20" y="{y}" xml:space="preserve">{line}</text>')
            
        svg.append('</g>')
        svg.append('</svg>')
        return "\n".join(svg)

    # 6. Save SVGs
    with open("github-metrics-dark.svg", "w") as f:
        f.write(generate_svg("dark"))
        
    with open("github-metrics-light.svg", "w") as f:
        f.write(generate_svg("light"))

    # 7. Update README.md
    with open("README.template.md", "r") as f:
        template = f.read()
        
    with open("README.md", "w") as f:
        f.write(template)

if __name__ == "__main__":
    main()
