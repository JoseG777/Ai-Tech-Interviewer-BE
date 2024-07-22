import requests


def getLeetCodeInfo(username):
    query = f"""
    {{
        matchedUser(username: "{username}") {{
            username
            submitStats: submitStatsGlobal {{
                acSubmissionNum {{
                    difficulty
                    count
                    submissions
                }}
            }}
        }}
    }}
  """

    url = "https://leetcode.com/graphql"

    response = requests.post(url, json={"query": query})

    if response.status_code == 200:
        data = response.json()
        test = [
            [
                stats["difficulty"],
                average(int(stats["count"]), int(stats["submissions"])),
            ]
            for stats in data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
        ]
        return test[0][1], test[1][1], test[2][1], test[3][1]
    else:
        print(
            f"Query failed to run by returning code of {response.status_code}. {response.text}"
        )


def average(count, submissions):
    if submissions == 0:
        return 0
    ratio = count / submissions
    return round(ratio, 2)


# print(getLeetCodeInfo("JoseG7"))
