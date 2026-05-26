import os
import urllib.request
import json
from datetime import date, datetime, timezone, timedelta
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
    
    # 2. Working On (Latest PushEvent)
    working_on = "N/A"
    events = []
    try:
        events = fetch_json(f"https://api.github.com/users/{username}/events/public", token)
        for event in events:
            if event.get("type") == "PushEvent":
                repo_full_name = event["repo"]["name"]
                if repo_full_name != f"{username}/{username}":
                    working_on = repo_full_name.split("/")[-1]
                    break
    except Exception:
        pass
        
    today_commits = 0
    today_repos = set()
    today_prs = 0
    today_issues = 0
    today_stars = 0
    recent_activity = []
    
    try:
        now = datetime.now(timezone.utc)
        one_day_ago = now - timedelta(days=1)
        for event in events:
            event_time = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if event_time < one_day_ago:
                continue
                
            etype = event.get("type")
            repo_name = event["repo"]["name"]
            
            if etype == "PushEvent":
                size = event["payload"].get("size", 1)
                today_commits += size
                r_name = repo_name.split("/")[-1]
                today_repos.add(r_name)
                
                ist_time = event_time + timedelta(hours=5, minutes=30)
                time_str = ist_time.strftime("%H:%M IST")
                
                commits_list = event["payload"].get("commits", [])
                if commits_list:
                    for c in commits_list:
                        sha = c.get("sha", "")[:7]
                        msg = c.get("message", "").split("\n")[0]
                        recent_activity.append((sha, msg, r_name, time_str))
                else:
                    head_sha = event["payload"].get("head")
                    msg = f"Pushed {size} commit(s)"
                    if head_sha:
                        try:
                            commit_info = fetch_json(f"https://api.github.com/repos/{repo_name}/commits/{head_sha}", token)
                            msg = commit_info["commit"]["message"].split("\n")[0]
                        except Exception:
                            pass
                    push_id = head_sha[:7] if head_sha else str(event["payload"].get("push_id", "Push"))[:7]
                    recent_activity.append((push_id, msg, r_name, time_str))
            elif etype == "PullRequestEvent" and event["payload"].get("action") in ["opened", "closed"]:
                today_prs += 1
            elif etype == "IssuesEvent" and event["payload"].get("action") in ["opened", "closed"]:
                today_issues += 1
            elif etype == "WatchEvent" and event["payload"].get("action") == "started":
                today_stars += 1
    except Exception:
        pass
    
    # 3. Repos (for stars and LOC)
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
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
              }
            }
          }
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
        
        weeks = contrib_collection["contributionCalendar"]["weeks"]
        days = []
        for week in weeks:
            days.extend(week["contributionDays"])
        last_14_days = days[-14:]
        counts = [day["contributionCount"] for day in last_14_days]
        
        ticks = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        max_val = max(counts) if counts else 0
        sparkline = ""
        for count in counts:
            if max_val == 0:
                sparkline += ticks[0]
            else:
                idx = int((count / max_val) * 7)
                sparkline += ticks[idx]
    except Exception as e:
        commits = "N/A"
        prs = "N/A"
        contrib = "N/A"
        sparkline = "              "

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

    # 6. Format Lines Dynamically
    TOTAL_WIDTH = 82

    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def pad_line(label, value):
        left = f". {label}: "
        right = f" {value}"
        dots = "." * max(1, (TOTAL_WIDTH - len(left) - len(right)))
        return f'<tspan class="dots">. </tspan><tspan class="label">{esc(label)}: </tspan><tspan class="dots">{dots}</tspan><tspan class="value">{esc(right)}</tspan>'

    def pad_double(label1, val1, label2, val2):
        half = (TOTAL_WIDTH - 3) // 2
        left1 = f". {label1}: "
        right1 = f" {val1}"
        dots1 = "." * max(1, half - len(left1) - len(right1))
        
        t_p1 = f'<tspan class="dots">. </tspan><tspan class="label">{esc(label1)}: </tspan><tspan class="dots">{dots1}</tspan><tspan class="value">{esc(right1)}</tspan>'
        len_p1 = len(left1) + len(dots1) + len(right1)
        
        left2 = f"{label2}: "
        right2 = f" {val2}"
        rem = TOTAL_WIDTH - len_p1 - 3
        dots2 = "." * max(1, rem - len(left2) - len(right2))
        
        t_p2 = f'<tspan class="label">{esc(label2)}: </tspan><tspan class="dots">{dots2}</tspan><tspan class="value">{esc(right2)}</tspan>'
        
        return f'{t_p1}<tspan class="dots"> | </tspan>{t_p2}'

    def make_header(title):
        base = f"- {title} "
        dashes = "-" * max(1, TOTAL_WIDTH - len(base))
        return f'<tspan class="header">{esc(base)}{dashes}</tspan>'
        
    def make_top_header(title, right_text):
        base = f"{title} "
        right = f" ({right_text})"
        dashes = "-" * max(1, (TOTAL_WIDTH - len(base) - len(right)))
        return f'<tspan class="header">{esc(base)}{dashes}{esc(right)}</tspan>'

    def pad_activity(label, sparkline_str):
        left = f". {label}: "
        right = f" [{sparkline_str}]"
        dots = "." * max(1, (TOTAL_WIDTH - len(left) - len(right)))
        return f'<tspan class="dots">. </tspan><tspan class="label">{esc(label)}: </tspan><tspan class="dots">{dots} [</tspan><tspan class="header">{esc(sparkline_str)}</tspan><tspan class="dots">]</tspan>'

    lines = [
        make_top_header("shreyash@swami", current_date_str),
        pad_line("OS", "Windows 11, Linux (Fedora)"),
        pad_line("Uptime", uptime_str),
        pad_line("IDE", "VSCode, Antigravity, IntelliJ"),
        pad_line("Status", "Open For Work"),
        '<tspan class="dots">.</tspan>',
        pad_line("Working.on", working_on),
        '<tspan class="dots">.</tspan>',
        pad_line("Languages.Programming", "JavaScript, Java, Python"),
        pad_line("Languages.Real", "English, Hindi"),
        '<tspan class="dots">.</tspan>',
        pad_line("Hobbies.Software", "Web-Dev, AI, Cloud"),
        pad_line("Hobbies.Hardware", "Table-Tennis, Reading"),
        '<tspan class="dots">.</tspan>',
        make_header("Contact"),
        pad_line("Email", "shreyash.swami2476@gmail.com"),
        pad_line("LinkedIn", "in/shreyashswami"),
        '<tspan class="dots">.</tspan>',
        make_header("GitHub-Stats"),
        pad_double("Repos", f"{fmt(public_repos)} [Contrib: {fmt(contrib)}]", "Stars", fmt(stars)),
        pad_double("Commits", fmt(commits), "Followers", fmt(followers)),
        pad_double("Pull.Requests", fmt(prs), "Lines.of.Code", f"~{fmt(total_loc)}"),
        pad_activity("Activity.(14d)", sparkline),
    ]
    
    if any([today_commits, today_prs, today_issues, today_stars]):
        lines.append('<tspan class="dots">.</tspan>')
        lines.append(make_header("Today.(Last.24h)"))
        
        if today_commits > 0:
            repos_str = ", ".join(today_repos)
            if len(repos_str) > 40:
                repos_str = f"{len(today_repos)} repositories"
            lines.append(pad_line("Pushed", f"{today_commits} commits to {repos_str}"))
            
            for sha, msg, repo, tstr in recent_activity:
                right_part = f" {repo} @ {tstr}"
                avail_msg = TOTAL_WIDTH - len(f".    > [{sha}] ") - len(right_part) - 3
                
                if len(msg) > avail_msg:
                    msg = msg[:max(0, avail_msg)]
                
                left_for_calc = f".    > [{sha}] {msg} "
                dots = "." * max(1, TOTAL_WIDTH - len(left_for_calc) - len(right_part))
                
                rendered_left = f"   > [{sha}] {msg} "
                lines.append(f'<tspan class="dots">. </tspan><tspan class="muted">{esc(rendered_left)}</tspan><tspan class="dots">{dots}</tspan><tspan class="muted">{esc(right_part)}</tspan>')
            
        if today_prs > 0:
            lines.append(pad_line("Pull.Requests", f"Worked on {today_prs} PR(s)"))
            
        if today_issues > 0:
            lines.append(pad_line("Issues", f"Worked on {today_issues} issue(s)"))
            
        if today_stars > 0:
            lines.append(pad_line("Starred", f"{today_stars} repo(s)"))

    def generate_svg(theme):
        bg_color = "#0d1117" if theme == "dark" else "#ffffff"
        label_color = "#58a6ff" if theme == "dark" else "#0969da"
        dots_color = "#484f58" if theme == "dark" else "#d0d7de"
        value_color = "#c9d1d9" if theme == "dark" else "#24292f"
        header_color = "#3fb950" if theme == "dark" else "#1a7f37"
        muted_color = "#8b949e" if theme == "dark" else "#57606a"
        
        height = 18 * len(lines) + 40
        
        svg = [
            f'<svg width="100%" viewBox="0 0 650 {height}" xmlns="http://www.w3.org/2000/svg">',
            f'<style>',
            f'  .text {{ font-family: "Courier New", Courier, monospace; font-size: 12px; }}',
            f'  .label {{ fill: {label_color}; font-weight: bold; }}',
            f'  .dots {{ fill: {dots_color}; }}',
            f'  .value {{ fill: {value_color}; }}',
            f'  .header {{ fill: {header_color}; font-weight: bold; }}',
            f'  .muted {{ fill: {muted_color}; }}',
            f'</style>',
            f'<rect width="100%" height="100%" fill="{bg_color}" rx="10" />',
            f'<g class="text">'
        ]
        
        for i, line in enumerate(lines):
            y = 30 + i * 18
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
    readme_content = """<picture>
  <source media="(prefers-color-scheme: dark)" srcset="github-metrics-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="github-metrics-light.svg">
  <img alt="GitHub Metrics Console" src="github-metrics-dark.svg" width="100%">
</picture>"""
        
    with open("README.md", "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()
