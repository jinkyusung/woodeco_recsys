import utils
from pprint import pprint


completion = utils.load_pickle("./_result/haliocination_and_information_update_issue.pkl")
# print(completion.choices[0].message.content)

completion = utils.load_pickle("./_result/nonoptimal_path_issue.pkl")
print(completion.choices[0].message.content)