import requests
import logging


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

    try:
        response = requests.post(url, json={"query": query})
        response.raise_for_status()

        data = response.json()
        if "errors" in data:
            logging.error(f"GraphQL errors: {data['errors']}")
            return "N/A"

        stats = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
        ratios = [
            average(int(stat["count"]), int(stat["submissions"])) for stat in stats
        ]
        return ratios[0], ratios[1], ratios[2], ratios[3]
    except requests.RequestException as re:
        logging.error(f"RequestException: {str(re)}")
        return "N/A"
    except KeyError as ke:
        logging.error(f"KeyError: {str(ke)}")
        return "N/A"
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return "N/A"


def average(count, submissions):
    if submissions == 0:
        return 0
    ratio = count / submissions
    return round(ratio, 2)
