from openai import OpenAI
import utils

################ API Keys ################
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
##########################################
client = OpenAI(api_key=OPENAI_API_KEY)


# default_content = \
# """Please make a date course within walking distance of Sinchon.
# Be sure to include the specific store name. 
# And Consider that a date is going to start at 5PM.
# Return message type must be json."""

# completion = client.chat.completions.create(
#   model="gpt-4-turbo",
#   messages=[
#     {"role": "system", "content": "You are an assistant who creates a specific dating course based on the given conditions."},
#     {"role": "user", "content": default_content}
#   ],
#   response_format={"type": "json_object"}
# )

# utils.save_pickle(completion, "./_result/default_content.pkl")


# content_with_distance = \
# """Please make a date course within walking distance of Sinchon.
# Be sure to include the specific store name. 
# Consider that a date is going to start at 5PM and Minimize inefficient overall movement of generated course.
# Return message type must be json."""

# completion = client.chat.completions.create(
#   model="gpt-4-turbo",
#   messages=[
#     {"role": "system", "content": "You are an assistant who creates a specific dating course based on the given conditions."},
#     {"role": "user", "content": content_with_distance}
#   ],
#   response_format={"type": "json_object"}
# )

# utils.save_pickle(completion, "./_result/nonoptimal_path_issue.pkl")


# content_with_distance = \
# """Please make a date course within walking distance of Sinchon.
# Be sure to include the specific store name. 
# Consider that a date is going to start at 5PM and Minimize inefficient overall movement of generated course.
# Return message type must be json."""

# completion = client.chat.completions.create(
#   model="gpt-4-turbo",
#   messages=[
#     {"role": "system", "content": "You are an assistant who creates a specific dating course based on the given conditions."},
#     {"role": "user", "content": content_with_distance}
#   ],
#   response_format={"type": "json_object"}
# )