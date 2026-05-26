import os
import urllib.request
import json
import time
from datetime import date

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

    with open("README.template.md", "r") as f:
        template = f.read()

    def fmt(n):
        return f"{n:,}" if isinstance(n, int) else str(n)

    # Format into template
    template = template.replace("{repos}", f"{fmt(public_repos):<3}")
    template = template.replace("{contrib}", f"{fmt(contrib):<3}")
    template = template.replace("{stars}", f"{fmt(stars):>5}")
    template = template.replace("{commits}", f"{fmt(commits):>6}")
    template = template.replace("{followers}", f"{fmt(followers):>5}")
    template = template.replace("{prs}", f"{fmt(prs):>6}")
    template = template.replace("{loc}", f"~{fmt(total_loc):>5}")
    template = template.replace("{uptime}", uptime_str)
    template = template.replace("{current_date}", current_date_str)

    with open("README.md", "w") as f:
        f.write(template)

if __name__ == "__main__":
    main()
